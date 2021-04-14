#!/usr/bin/env bash

__ScriptVersion="0.0.1"

#===  FUNCTION  ================================================================
#         NAME:  usage
#  DESCRIPTION:  Display usage information.
#===============================================================================
function usage ()
{
    echo "Usage :  $0 [options] [--] nqDirectoryy

    Options:
    -h|help       Display this message
    -v|version    Display script version"

}    # ----------  end of function usage  ----------

#-----------------------------------------------------------------------
#  Handle command line arguments
#-----------------------------------------------------------------------

while getopts ":hv" opt
do
  case opt in

    h|help     )  usage; exit 0   ;;

    v|version  )  echo "$0 -- Version __ScriptVersion"; exit 0   ;;

    * )  echo -e "\n  Option does not exist : OPTARG\n"
                usage; exit 1   ;;

  esac    # --- end of case ---
done
shift $((OPTIND-1))

DIR=$1

if [[ ! -d "$DIR" ]]; then

    echo "Given directory of benchmark csv files doesn't exists: $DIR" 
    exit 1
fi


for file in "$DIR/*.csv"; 
do 
    echo "Sorting $file..."
    sort -o $file $file 
done
sort -m *.csv > final_output.csv  
