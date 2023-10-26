#!/bin/bash

fd=$1 #which foundation, eclipse or mozilla or apache
embdir="m.embVector/glove"
pdir="m.afterPreprocess"
unit=5000 #process every 5000 bug report by glove each time

for d in 50 100 200 300 #three dimensions for fasttext
do
    mkdir -p ${embdir}/${d}/${fd}
done

for f in ${pdir}/${fd}/*
do
    fname=$(echo ${f} | awk -F "/" '{print $NF}')
    echo $fname

    startL=1
    brCnt=$(cat ${f} | wc -l)
    echo ${f}": no available word embeddings for its token after checked against pre-trained model" >>${fd}.glove.nullBR
    while [ $startL -le $brCnt ]
    do
            endL=$((startL + unit -1))
            min=$([ $endL -le $brCnt ] && echo "$endL" || echo "$brCnt")
            echo $startL $min $brCnt
            sed -n "${startL},${min}P" ${f} > $fd.glove.tmp
            startL=$((endL+1))
            #break
            
            #run glove 100, 200, and 300 for the same bat BRs
            for d in 50 300 100 200
            do
                dres=${embdir}/${d}/${fd}
                ./glove-retrieve-emb.sh glove/glove.6B.${d}d.txt $fd.glove.tmp $d > $fd.glove.emb
                ./avg-max-pooling.sh $fd.glove.emb ${fd}.glove.nullBR > $fd.glove.pooling
                cut -f1,2 -d "," $fd.glove.pooling >> ${dres}/emb.${fname}.avgpooling
                cut -f1,3 -d "," $fd.glove.pooling >> ${dres}/emb.${fname}.maxpooling
                #break
            done
            #break
    done
    #break
done
