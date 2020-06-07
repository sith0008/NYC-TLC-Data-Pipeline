# NYC-TLC-Data-Pipeline

This is a data engineering project which takes in streaming trip data generated from the NYC TLC trip records dataset, and performs real-time processing as well as batch processing. 

## Overview

This project consists of 3 main portions: data ingestion, processing as well as visualization. The data flow is shown in the architecture diagram below. 

![alt text](https://github.com/sith0008/NYC-TLC-Data-Pipeline/blob/master/architecture.png?raw=true)

### Step 0: Preprocessing

As the dataset used is somewhat processed, a Python script was used to process the data back to its unprocessed form. Specifically, each trip record is separated into 2 records indicating the start of a trip and the end of a trip.

### Step 1: Data ingestion

To simulate streaming data, I built a Golang client which constantly sends in trip records to a Golang server developed using the gorilla-mux framework. The server then acts as a Kafka producer, publishing streams onto the Kafka server. 

### Step 2: Storage and processing

There are 2 direct consumers of the Kafka streams -- storage and real-time processor. I wrote a Golang script to read messages from the Kafka topics and store the data into PostgreSQL. Simultaneously, I used Spark Streaming to process the data in real-time. 

[Work-in-Progress] After storage, a batch processor built using Spark and scheduled using Airflow processes the data in batches (daily / weekly / monthly aggregations)

### Step 3: Visualization

The processors send the processed data in the form of JSON objects to a Flask app, which renders a dashboard built using Chart.js. 


## Requirements

- Zookeeper 
- Kafka
- Go
- Spark
- PostgreSQL
- Flask

## Usage

# Kafka server setup

Kafka relies on Zookeeper for maintaining configuration information, so we have to start up the Zookeeper server first.
```bash
./kafka/bin/zookeeper-server-start.sh ./kafka/config/zookeeper.properties
```
```bash
./kafka/bin/kafka-server-start.sh ./kafka/config/server.properties
```

# Flask app setup

Before streaming, start the Flask app. 

```bash
cd dashboard
flask run
```

# Consumer setup

Start the storage consumer
```bash
cd consumer_store
go run store.go
```

Start the processing consumer
```bash
cd consumer_process
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.5 process.py
```

# Producer setup

Initialize server to handle incoming requests
```bash
cd producer
go run producer-server.go
```

Run client to send requests
```bash
go run producer-client.go
```




