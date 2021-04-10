#!/usr/bin/env bash


function divider() {
    local char=$1
    if [[ -z "${1+x}" ]]; then
       char="=" 
    fi
    echo "" 
    printf "${char}%.0s"  $(seq 1 63) 
    echo "" 
}


function cleanup() {
    #function_body
    divider
    echo "Cleaning up..." 
    docker-compose stop 
    exit 1 
}

IP_ADDR=$(hostname -I | head -n1 | awk '{print $1}')

echo "IP_ADDR=$IP_ADDR" > resources/.custom_env 

trap cleanup SIGHUP SIGINT SIGTERM

divider 
echo "Starting up necessary docker containers for Kafka and Flink..." 
divider 
docker-compose --env-file .custom_env up -d 
divider 

