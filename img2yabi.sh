#!/bin/bash
filet=0
filei=0
extname="*.tif"
mkdir yabi
for file in $extname
do
    filet=`expr $filet + 1`
done
for file in $extname
do
    filei=`expr $filei + 1`
    echo "[$filei/$filet] $file -> ${file%%.*}.yabi";
    python3 img2yabi.py 1 "$file" "yabi/${file%%.*}.yabi"
done