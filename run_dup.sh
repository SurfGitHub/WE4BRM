#!/bin/bash
embDir="embVector"
top10Dir="top10"
resDir="dupCosineRankRes"
mkdir -p $resDir
fd=$1
ptype=$2 # max or avg pooling
#f format:bugID,keyID,label,labelOriValue(if exists), we use keyId in emb dat files
for f in ${top10Dir}/${fd}/*.closedBugs
do
    pname=$(echo ${f} | awk -F "/" '{print $NF}' | cut -f1 -d ".") #get product name

    if [[ $pname == "Platform" ]]; then
       echo $pname":too large skip now"
       continue
    fi
    for emb in ${embDir}/*/*/${fd}/*_${pname}.csv.${ptype}*
    do
        we=$(echo ${emb} | awk -F "/" '{print $2}') #get embedding model 
        d=$(echo ${emb} | awk -F "/" '{print $3}') #get embedding vector dimension 
        python dup.py ${f} ${emb} ${resDir}/${fd}.${pname}.${ptype}.${we}.${d}.cosDupRanks
    done
    #break
done
