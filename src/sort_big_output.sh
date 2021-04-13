#!/usr/bin/env bash


for file in *.nq; 
do 
    echo "Sorting $file..."
    sort -o $file $file 
done
sort -m *.nq | split -d -1 10000 - output
