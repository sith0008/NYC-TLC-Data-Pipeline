import geopandas as gpd
import pandas as pd
from tqdm import tqdm
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np

def main():
    # part 1: split start and end
    df = pd.read_csv('train.csv')
    start = df[['id','vendor_id','pickup_datetime','pickup_longitude','pickup_latitude']]
    end = df[['id','vendor_id','dropoff_datetime','dropoff_longitude','dropoff_latitude']]
    start.columns = ['id','vendor_id','datetime','longitude','latitude']
    end.columns = ['id','vendor_id','datetime','longitude','latitude']
    start['status'] = 'start'
    end['status'] = 'end'
    main = start.append(end)
    main = main.sort_values('datetime')
    # part 2: add zones
    zones = gpd.read_file('taxi_zones.shp')
    geom = main.apply(lambda x : Point([x.longitude,x.latitude]),axis=1)
    main = gpd.GeoDataFrame(main, geometry = geom)
    main.crs = {'init' :'epsg:4326'}
    zones = zones.to_crs({'init': 'epsg:4326'})
    merged = gpd.sjoin(main, zones[['zone','geometry']], op='within')
    merged = merged.drop(['geometry','index_right'],axis=1)
    merged = merged.sort_values('datetime')
    merged.to_csv('../data/trips.csv',index=False)

if __name__ == '__main__':
    main()