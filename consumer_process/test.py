from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.context import SQLContext
from pyspark.sql.types import *
from pyspark.sql.functions import *
import json
import requests
import geopandas as gpd
from shapely.geometry import Point, Polygon, shape
import shapely.speedups
shapely.speedups.enable() # this makes some spatial queries run faster

conf = SparkConf()
conf.setAppName('realTimeProcessor')
sc = SparkContext(conf=conf)
sc.setLogLevel('WARN')
sql_context = SQLContext(sc)
spark = SparkSession.builder.appName('realTimeProcessor').getOrCreate()

start_df = spark.read.format('csv') \
    .option('header','true') \
    .option('inferSchema','true') \
    .load('../data/train_processed.csv') \
    .limit(100)
zones = gpd.read_file('../data/taxi_zones.shp')
sc.broadcast(zones)

def map_point_to_zone(longitude, latitude):
    gdf = zones.apply(lambda x: x['id'] if x['geometry'].intersects(Point(longitude, latitude)) else None, axis=1)
    idx = gdf.first_valid_index()
    first_valid_value = gdf.loc[idx] if idx is not None else None
    return first_valid_value

map_udf = udf(map_point_to_zone)
start_df = start_df.withColumn("zone_id", map_udf(col("longitude"),col("latitude")))
start_df.show()
# start_df.printSchema()