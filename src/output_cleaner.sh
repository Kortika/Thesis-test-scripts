#!/usr/bin/env bash


for file in *.nq ; do
    cleaned_file="${file}_cleaned"

    grep -oP "lane[0-9]+.*?timestamp.*?>" $file | paste -d " "  - - | sed -E "s/\?|\&| /,/g" > $cleaned_file 
    sed -i "s/[<>]//g" $cleaned_file
    sed -i "s/%20/ /g" $cleaned_file
    sed -i "s/%3A/ /g" $cleaned_file
    sed -i "s/-/ /g" $cleaned_file
    sed -i -E "s/[a-z]+=//g" $cleaned_file
    awk -F"," '{OFS=","; $6=mktime($6); $13=mktime($13); print $0}'  $cleaned_file > .tmp 
    mv .tmp $cleaned_file
done
