#!/bin/bash

##note that, since we also retrieve word2vec300.txt as glove.6B.300d.txt. hence, we can use the same way to obtain max/avg-pooling as for glove
fd=$1 #which foundation, eclipse or mozilla or apache
embdir="m.embVector/word2vec"
pdir="m.afterPreprocess"
unit=5000 #process every 5000 bug report by word2vec each time

for d in 300 #word2vec only run 300 currently.
do
    mkdir -p ${embdir}/${d}/${fd}
done

for f in ${pdir}/${fd}/*
do
    fname=$(echo ${f} | awk -F "/" '{print $NF}')
    echo $fname

    startL=1
    brCnt=$(cat ${f} | wc -l)
    echo ${f}": no available word embeddings for its token after checked against pre-trained model" >>${fd}.word2vec.nullBR
    while [ $startL -le $brCnt ]
    do
            endL=$((startL + unit -1))
            min=$([ $endL -le $brCnt ] && echo "$endL" || echo "$brCnt")
            echo $startL $min $brCnt
            sed -n "${startL},${min}P" ${f} > $fd.word2vec.tmp
            startL=$((endL+1))
            
            #run word2vec 300 only for the same bat BRs currently
            for d in 300
            do
                dres=${embdir}/${d}/${fd}
                ./glove-retrieve-emb.sh word2vec${d}.txt $fd.word2vec.tmp $d > $fd.word2vec.emb
                ./avg-max-pooling.sh $fd.word2vec.emb ${fd}.word2vec.nullBR > $fd.word2vec.pooling
                cut -f1,2 -d "," $fd.word2vec.pooling >> ${dres}/emb.${fname}.avgpooling
                cut -f1,3 -d "," $fd.word2vec.pooling >> ${dres}/emb.${fname}.maxpooling
                #break
            done
            #break
    done
    #break
done
