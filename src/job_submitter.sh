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

__ScriptVersion="0.0.1"

#===  FUNCTION  ================================================================
#         NAME:  usage
#  DESCRIPTION:  Display usage information.
#===============================================================================
function usage ()
{
    echo "Usage :  $0 -m mappfile -o outputPath [options] [--]

    Required: 
    -m|mapping-file     Location of mapping file on the local machine 
    -o|output-path      Location of the output file/folder in the jobmanager's container

    Options:
    -c|compile          Flag to determine if there is a need to compile RMLStreamer 
    -h|help             Display this message
    -v|version          Display script version"

}    # ----------  end of function usage  ----------

#-----------------------------------------------------------------------
#  Handle command line arguments
#-----------------------------------------------------------------------

while getopts ":hvcm:o:" opt
do
    case $opt in
        m|mapping-file ) 
            MAPPING_FILE_PATH=$OPTARG ;; 
        o|output-path ) 
            OUTPUT_PATH=$OPTARG ;; 

        c|compile ) 
            COMPLE_FLAG=1 ;; 

        h|help     )  usage; exit 0   ;;

        v|version  )  echo "$0 -- Version $__ScriptVersion"; exit 0   ;;

        \? ) echo "Unknown option: -$OPTARG" >&2; exit 1;;

        :  ) echo "Missing option argument for -$OPTARG" >&2; exit 1;;

        * )  echo -e "\n  Option does not exist : $OPTARG\n"
              usage; exit 1   ;;

    esac    # --- end of case ---
done
shift $(($OPTIND-1))
${MAPPING_FILE_PATH:?Missing mapping file -m}
${OUTPUT_PATH:?Missing output path -o}


divider
if [[ "${COMPLE_FLAG+x}" ]]; then
    
    CURRENT_DIR="$(pwd)" 
    RML_STREAMER_REPO="../rml-streamer"

    echo "Compiling RMLStreamer from the path ${RML_STREAMER_REPO}" 
    divider

    cd $RML_STREAMER_REPO
    mvn -DskipTests clean package 
    cp -f target/RMLStreamer*.jar "${CURRENT_DIR}/resources/"
    cd $CURRENT_DIR
else 

    echo "Skipping compilation of RMLStreamer..." 
    divider 

fi


BASE_DATA_PATH="/mnt/data/"
MAPPING_FILE_CONTAINER_PATH="${BASE_DATA_PATH}${MAPPING_FILE_PATH##*/}" 
OUTPUT_PATH="${BASE_DATA_PATH}${OUTPUT_PATH}"

JOB_CLASS_NAME="io.rml.framework.Main"
JM_CONTAINER=$(docker ps --filter name=jobmanager --format={{.ID}})

docker cp $MAPPING_FILE_PATH "${JM_CONTAINER}:${BASE_DATA_PATH}"
docker cp resources/RMLStreamer-2.0.1-SNAPSHOT.jar  "${JM_CONTAINER}":/job.jar
docker exec -t -i "${JM_CONTAINER}" flink run -d -c ${JOB_CLASS_NAME} /job.jar toFile --bulk --mapping-file $MAPPING_FILE_CONTAINER_PATH --output-path $OUTPUT_PATH  

