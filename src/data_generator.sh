#!/usr/bin/env bash

__ScriptVersion="0.0.1"
#===  FUNCTION  ================================================================
#         NAME:  usage
#  DESCRIPTION:  Display usage information.
#===============================================================================
function usage ()
{
    echo "Usage :  $0 [options] [--]

    Options:
    -m|mode       Stream mode of data generator. Following options are valid:
                  "single-burst" 
                  "periodic-burst" 
                  "constant-rate" 
    -h|help       Display this message
    -v|version    Display script version"

}    # ----------  end of function usage  ----------

#-----------------------------------------------------------------------
#  Handle command line arguments
#-----------------------------------------------------------------------

while getopts ":hvm:" opt
do
  case $opt in
    m|mode     ) 
        case $OPTARG in 

            constant-rate ) 
                STREAM_MODE="constant-rate";;

            single-burst )
                STREAM_MODE="single-burst";;

            periodic-burst )
                STREAM_MODE="periodic-burst";; 

            * ) 
                usage; exit 1;; 
                
        esac;;

    h|help     )  usage; exit 0   ;;

    v|version  )  echo " -- Version $__ScriptVersion"; exit 0   ;;

    \? ) echo "Unknown option: -$OPTARG" >&2; exit 1;;

    :  ) echo "Missing option argument for -$OPTARG" >&2; exit 1;;

    * )  echo -e "\n  Option does not exist : $OPTARG\n"
          usage; exit 1   ;;

  esac    # --- end of case ---
done
shift $(($OPTIND-1))

if [[ -z "${STREAM_MODE+x}" ]]; then
   echo "Defaulting to data generation mode with constant-rate";
   STREAM_MODE="constant-rate";
fi

IP_ADDR=$(hostname -I | head -n1 | awk '{print $1}')
#sleep for 10 seconds just to get docker setup ready and running
export S3_ACCESS_KEY=xxx # S3 access key of data input
export S3_SECRET_KEY=xxx # S3 secret key of data input
export KAFKA_BOOTSTRAP_SERVERS=$IP_ADDR:9092  # list of Kafka brokers in the form of "host1:port1,host2:port2"
export DATA_VOLUME=0 # inflation factor for the data

#possible modes:    constant-rate
#                   single-burst
#                   periodic-burst
#                   faulty-event

export MODE=$STREAM_MODE # data characteristics of the input stream (explained further)
export FLOWTOPIC=ndwflow # Kafka topic name for flow data
export SPEEDTOPIC=ndwspeed # Kafka topic name for speed data
export RUNS_LOCAL=true # whether we run locally or on a platform

cd include/open-stream-processing-benchmark/data-stream-generator

sbt compile 
sbt run 



