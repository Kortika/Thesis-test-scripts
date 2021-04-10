#!/usr/bin/env bash

echo "IP_ADDR=$(hostname -I | head -n1 | awk '{print $1}')" > .env 

docker-compose up -d 

rm .env

#sleep for 10 seconds just to get docker setup ready and running
sleep 10 
export S3_ACCESS_KEY=xxx # S3 access key of data input
export S3_SECRET_KEY=xxx # S3 secret key of data input
export KAFKA_BOOTSTRAP_SERVERS=$(hostname -I | head -n1 | awk '{print $1}'):9092  # list of Kafka brokers in the form of "host1:port1,host2:port2"
export DATA_VOLUME=0 # inflation factor for the data
export MODE=constant-rate # data characteristics of the input stream (explained further)
export FLOWTOPIC=ndwflow # Kafka topic name for flow data
export SPEEDTOPIC=ndwspeed # Kafka topic name for speed data
export RUNS_LOCAL=true # whether we run locally or on a platform

cd include/open-stream-processing-benchmark/data-stream-generator

sbt compile 
sbt run 
