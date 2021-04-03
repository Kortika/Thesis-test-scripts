#!/usr/bin/bash

__ScriptVersion="0.1"

#===  FUNCTION  ================================================================
#         NAME:  usage
#  DESCRIPTION:  Display usage information.
#===============================================================================
function usage ()
{
    echo "Usage :  $0 [options] file

    Options:
    [file]          A yaml file which contains the setup for 
                    Apache Kafka inc zookeeper
    -h|help         Display this message
    -v|version      Display script version"

}    # ----------  end of function usage  ----------

#-----------------------------------------------------------------------
#  Handle command line arguments
#-----------------------------------------------------------------------

while getopts ":f:hv" opt
do
  case $opt in
    h|help     )  usage; exit 0   ;;

    v|version  )  echo "$0 -- Version $__ScriptVersion"; exit 0   ;;

    \? ) echo "Unknown option: -$OPTARG" >&2; exit 1;;

    :  ) echo "Missing option argument for -$OPTARG" >&2; exit 1;;

    * )  echo -e "\n  Option does not exist : $OPTARG\n"
          usage; exit 1   ;;

  esac    # --- end of case ---
done

shift $(($OPTIND-1))

if [[ ! -f  $1 ]]; then
   echo "Yaml file needs to be provided!" >&2
   usage
   exit 1 
fi

KAKFA_DOCKER_YAML="$1"

#Run docker yaml to setup kafka broker 
docker-compose -f $KAKFA_DOCKER_YAML up -d 


export KAFKA_BOOTSTRAP_SERVERS=$(hostname -i | head -n1 | awk '{print $1}'):9092  # list of Kafka brokers in the form of "host1:port1,host2:port2"
export DATA_VOLUME=0 # inflation factor for the data
export MODE=constant-rate # data characteristics of the input stream (explained further)
export FLOWTOPIC=ndwflow # Kafka topic name for flow data
export SPEEDTOPIC=ndwspeed # Kafka topic name for speed data
export RUNS_LOCAL=true # whether we run locally or on a platform
export S3_ACCESS_KEY=xxx # S3 access key of data input
export S3_SECRET_KEY=xxx # S3 secret key of data input


cd open-stream-processing-benchmark/data-stream-generator/ 

sbt compile 
sbt run

