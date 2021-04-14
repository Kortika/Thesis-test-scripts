#!/usr/bin/env bash
__ScriptVersion="0.0.1"

#===  FUNCTION  ================================================================
#         NAME:  usage
#  DESCRIPTION:  Display usage information.
#===============================================================================
function usage ()
{
    echo "Usage :  $0 [options] [--] nqDirectory

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

    v|version  )  echo "$0 -- Version opjt"; exit 0   ;;

    * )  echo -e "\n  Option does not exist : OPTARG\n"
                usage; exit 1   ;;

  esac    # --- end of case ---
done
shift $((OPTIND-1))

DIR="$1"

if [[ ! -d "$DIR" ]]; then 
	echo "Given directory of nq files doesn't exists: $DIR" 
	exit 1
fi

clean_file() {
    file="$1"
    local CLEANED_DIR="$2"
    echo "Cleanin file $file..."
    cleaned_file="${CLEANED_DIR}/${file##*/}.csv"
    grep -oP "lane[0-9]+.*?timestamp.*?>" $file | paste -d " "  - - | sed -E "s/\?|\&| /,/g" > $cleaned_file 
    sed -e "s/[<>]//g" -e "s/%20/ /g" -e "s/%3A/ /g" -e "s/-/ /g" -Ee "s/[a-z]+=//g" < $cleaned_file > "$1.tmp" 
    awk -F"," '{OFS=","; $6=mktime($6); $13=mktime($13); print $0}' "$1.tmp" > $cleaned_file 
    rm "$1.tmp"
}



CLEANED_DIR="${DIR}cleaned"

mkdir -p "$CLEANED_DIR"
N=10

(
for file in ${DIR}*.nq ; do
    ((i=i%N)); ((i++==0)) && wait
    clean_file $file $CLEANED_DIR &
done
)
