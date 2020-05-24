import pandas as pd

def main():
    df = pd.read_csv('train.csv')
    start = df[['id','vendor_id','pickup_datetime','pickup_longitude','pickup_latitude']]
    end = df[['id','vendor_id','dropoff_datetime','dropoff_longitude','dropoff_latitude']]
    start.columns = ['id','vendor_id','datetime','longitude','latitude']
    end.columns = ['id','vendor_id','datetime','longitude','latitude']
    start['status'] = 'start'
    end['status'] = 'end'
    main = start.append(end)
    main = main.sort_values('datetime')
    main.to_csv('train_processed.csv',index=False)

if __name__ == '__main__':
    main()