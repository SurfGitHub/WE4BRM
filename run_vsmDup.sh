#!/bin/bash
pdir="afterPreprocess"
top10Dir="top10"
resDir="vsmDupCosineRankRes"
mkdir -p $resDir
fd=$1
cuda=$2

for f in ${top10Dir}/${fd}/*.closedBugs
do
    pname=$(echo ${f} | awk -F "/" '{print $NF}' | cut -f1 -d ".") #get product name
    for p in ${pdir}/${fd}/*_${pname}.csv
    do
        echo $f $p
        awk 'BEGIN{FS="[, ]";OFS=" "}{if(NR<=FNR){arr[$2]=1}else{if($1 in arr){print $0}}}' ${f} ${p} > ${fd}.vsmp
        p_r_f=$(CUDA_VISIBLE_DEVICES=$cuda python vsm-dup.py ${f} ${fd}.vsmp ${resDir}/${fd}.${pname}.vsm.cosDupRanks)
	#break
    done
    #break
 done
