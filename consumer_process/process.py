from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.context import SQLContext
from pyspark.sql.types import *
from pyspark.sql.functions import *
import json
import requests
import pandas as pd

def read_process():
    trip_record_schema = StructType() \
        .add("TripID",StringType()) \
        .add("VendorID",IntegerType()) \
        .add("Datetime", StringType()) \
        .add("Latitude", FloatType()) \
        .add("Longitude", FloatType()) \
        .add("Status", StringType()) \
        .add("Zone", StringType())
    
    complete_trip_record_schema = StructType() \
        .add("TripID", StringType()) \
        .add("StartTime", StringType()) \
        .add("EndTime", StringType()) \
        .add("Status", StringType())

    start_df = spark.readStream \
        .format('kafka') \
        .option("kafka.bootstrap.servers","localhost:9092") \
        .option("subscribe","start") \
        .option("startingOffsets","latest") \
        .load()
    start_df = start_df.selectExpr("CAST(value AS STRING)","timestamp")
    start_df = start_df.select(from_json(col("value"), trip_record_schema).alias("trip_record"),"timestamp")
    start_df = start_df.select("trip_record.*","timestamp")
    start_df = start_df.withWatermark("timestamp","1 hour")
    end_df = spark.readStream \
        .format('kafka') \
        .option("kafka.bootstrap.servers","localhost:9092") \
        .option("subscribe","end") \
        .option("startingOffsets","latest") \
        .load()
    end_df = end_df.selectExpr("CAST(value AS STRING)","timestamp")
    end_df = end_df.select(from_json(col("value"), trip_record_schema).alias("trip_record"),"timestamp")
    end_df = end_df.select("trip_record.*","timestamp")
    end_df = end_df.withWatermark("timestamp","1 hour")

    complete_df = spark.readStream \
        .format('kafka') \
        .option('kafka.bootstrap.servers','localhost:9092') \
        .option('subscribe','complete') \
        .option("startingOffsets",'latest') \
        .load()
    complete_df = complete_df.selectExpr("CAST(value AS STRING)","timestamp")
    complete_df = complete_df.select(from_json(col("value"), complete_trip_record_schema).alias("complete_trip"),"timestamp")
    complete_df = complete_df.select("complete_trip.*","timestamp")

    return start_df, end_df, complete_df

def zone_aggregate_process(start_df, end_df, LIMIT):
    top_pickup_df = start_df.groupBy('zone').count().orderBy('count',ascending=False).limit(LIMIT)
    top_dropoff_df = end_df.groupBy('zone').count().orderBy('count',ascending=False).limit(LIMIT)
    return top_pickup_df, top_dropoff_df

def duration_process(complete_df):
    def get_duration(start_time, end_time):
        start_hour = int(start_time.split(' ')[1].split(':')[0])
        start_minute = int(start_time.split(' ')[1].split(':')[1])
        start_seconds = int(start_time.split(' ')[1].split(':')[2])
        end_hour = int(end_time.split(' ')[1].split(':')[0])
        end_minute = int(end_time.split(' ')[1].split(':')[1])
        end_seconds = int(end_time.split(' ')[1].split(':')[2])
        duration = end_hour*3600+end_minute*60+end_seconds-start_hour*3600-start_minute*60-start_seconds
        return duration
    def get_bins(duration):
        duration = int(duration)
        if duration <= 3600:
            return (duration / 60) // 5 + 1
        else:
            return 13
    bins_udf = udf(lambda x: get_bins(x))
    duration_udf = udf(lambda x, y: get_duration(x, y))
    complete_df = complete_df.withColumn('duration', duration_udf(complete_df['StartTime'],complete_df['EndTime']))
    complete_df = complete_df.withColumn('bin',bins_udf(complete_df['duration']))
    duration_hist_df = complete_df.groupBy('bin').count().orderBy('bin')
    return duration_hist_df

def write_process(top_pickup_df=None, top_dropoff_df=None, duration_hist_df=None):
    def send_top_regions(df, epoch_id):
        df.show()
    def send_duration(df, epoch_id):
        df.show()
    if top_pickup_df:
        top_pickup_stream = top_pickup_df.writeStream \
            .outputMode("complete") \
            .foreachBatch(send_top_regions) \
            .start()
    if top_dropoff_df:
        top_dropoff_stream = top_dropoff_df.writeStream \
            .outputMode("complete") \
            .foreachBatch(send_top_regions) \
            .start()
    if duration_hist_df:
        duration_stream = duration_hist_df.writeStream \
            .outputMode("complete") \
            .foreachBatch(send_duration) \
            .start()
    spark.streams.awaitAnyTermination()

def main():
    start_df, end_df, complete_df = read_process()
    top_pickup_df, top_dropoff_df = zone_aggregate_process(start_df, end_df, 10)
    duration_hist_df = duration_process(complete_df)
    write_process(top_pickup_df,top_dropoff_df,duration_hist_df)

if __name__ == '__main__':
    BATCH_INTERVAL = 2
    conf = SparkConf()
    conf.setAppName('realTimeProcessor')
    sc = SparkContext(conf=conf)
    sc.setLogLevel('WARN')
    sqlContext = SQLContext(sc)
    spark = SparkSession.builder.appName('realTimeProcessor').getOrCreate()
    ssc = StreamingContext(sc,BATCH_INTERVAL)
    main()