#!/bin/bash

fd=$1 #which foundation, eclipse or mozilla or apache
embdir="embVector/bert"
pdir="afterPreprocess"
unit=1000 #process every 5000 bug report by bert each time

for d in 768 #only run the most used 768
do
    mkdir -p ${embdir}/${d}/${fd}
done

for f in ${pdir}/${fd}/*
do
    fname=$(echo ${f} | awk -F "/" '{print $NF}')
    echo $fname

    startL=1
    brCnt=$(cat ${f} | wc -l)
    echo ${f}": no available word embeddings for its token after checked against pre-trained model" >>${fd}.bert.nullBR
    while [ $startL -le $brCnt ]
    do
            endL=$((startL + unit -1))
            min=$([ $endL -le $brCnt ] && echo "$endL" || echo "$brCnt")
            echo $startL $min $brCnt
            sed -n "${startL},${min}P" ${f} > $fd.bert.tmp
            startL=$((endL+1))
            #break
            
            #run bert 768 for the bat BRs defautly
            for d in 768
            do
                dres=${embdir}/${d}/${fd}
                python3 avg-max-bert.py $fd.bert.tmp $fd.bert.avgp $fd.bert.maxp
                cat $fd.bert.avgp >> ${dres}/emb.${fname}.avgpooling
                cat $fd.bert.maxp >> ${dres}/emb.${fname}.maxpooling
                #break
            done
            #break
    done
    #break
done

