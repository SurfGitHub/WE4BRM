#!/bin/bash

fd=$1 #which foundation, eclipse or mozilla or apache
embdir="m.embVector/fastText"
pdir="m.afterPreprocess"
unit=5000 #process every 5000 bug report by fastText each time

for d in 100 200 300 #three dimensions for fasttext
do
    mkdir -p ${embdir}/${d}/${fd}
done

for f in ${pdir}/${fd}/*
do
    fname=$(echo ${f} | awk -F "/" '{print $NF}')
    echo $fname

    startL=1
    brCnt=$(cat ${f} | wc -l)
    while [ $startL -le $brCnt ]
    do
            endL=$((startL + unit -1))
            min=$([ $endL -le $brCnt ] && echo "$endL" || echo "$brCnt")
            echo $startL $min $brCnt
            sed -n "${startL},${min}P" ${f} | awk '{if(NF>1){print $0}}' > $fd.fastText.tmp
            startL=$((endL+1))
            #break
            
            #run fastText 100, 200, and 300 for the same bat BRs
            for d in 300 100 200
            do
                dres=${embdir}/${d}/${fd}
                cat $fd.fastText.tmp | ./fasttext print-word-vectors cc.en.${d}.bin > $fd.fastText.emb
                ./avg-max-pooling.sh $fd.fastText.emb > $fd.fastText.pooling
                cut -f1,2 -d "," $fd.fastText.pooling >> ${dres}/emb.${fname}.avgpooling
                cut -f1,3 -d "," $fd.fastText.pooling >> ${dres}/emb.${fname}.maxpooling
                #break
            done
            #break
    done
    #break
done
