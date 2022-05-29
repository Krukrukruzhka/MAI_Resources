#!/bin/bash

cat /dev/null > output.txt

MAXSIZE=$1
SUFF=$2

find /home -type f -perm /a!=x -name "*"$SUFF | xargs ls -l | awk '{print $9 " " $5}' | while read line ; 

do
    len=${line}
    let filesize=$filesize+$len

    if [ $filesize -gt $MAXSIZE ];
    then
    	let filesize=$filesize-$len
    	exit
    fi

    echo $line >> output.txt
done
cat output.txt
wc -c output.txt