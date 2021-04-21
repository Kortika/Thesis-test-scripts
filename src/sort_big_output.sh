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
sort_file(){
    local file=$1
    local sortedDir=$2

    echo "Sorting $file..."
    sort -o "${sortedDir}${file##*/}_sorted"  $file
}

N=10
SORTED_DIR="${DIR}sorted/"
mkdir -p $SORTED_DIR 

(
for file in ${DIR}*.csv ; do
    ((i=i%N)); ((i++==0)) && wait
    sort_file $file $SORTED_DIR &
done
)
wait
sleep 5
echo "Done sorting sub files" 
echo "Merging files in ${SORTED_DIR}"
sort -m ${SORTED_DIR}*_sorted > final_output.csv  

