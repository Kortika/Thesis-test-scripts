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
docker-compose -f $KAKFA_DOCKER_YAML down 



