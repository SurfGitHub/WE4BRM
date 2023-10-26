#####!/bin/bash

fd=$1 #which foundation, eclipse or mozilla or apache
embdir="embVector/elmo"
pdir="afterPreprocess"
unit=1000 #process every 5000 bug report by elmo each time

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
    echo ${f}": no available word embeddings for its token after checked against pre-trained model" >>${fd}.elmo.nullBR
    while [ $startL -le $brCnt ]
    do
            endL=$((startL + unit -1))
            min=$([ $endL -le $brCnt ] && echo "$endL" || echo "$brCnt")
            echo $startL $min $brCnt
            sed -n "${startL},${min}P" ${f} > $fd.elmo.tmp
            startL=$((endL+1))
            #break
            
            #run elmo 768 for the bat BRs defautly
            for d in 768
            do
                dres=${embdir}/${d}/${fd}
                ###python avg-max-elmo.py $fd.elmo.tmp $fd.elmo.avgp $fd.elmo.maxp
                python test-elmo.py $fd.elmo.tmp $fd.elmo.avgp $fd.elmo.maxp
                cat $fd.elmo.avgp >> ${dres}/emb.${fname}.avgpooling
                cat $fd.elmo.maxp >> ${dres}/emb.${fname}.maxpooling
                break
            done
            break
    done
    break
done

