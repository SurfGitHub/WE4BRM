#!/bin/bash
embDir="embVector"
labelDir="label"
top10Dir="top10"
resDir="embMLRes.para"
mkdir -p $resDir
fd=$1
cuda=$2
ptype="avg"

#f format:bugID,taskValue,label
for f in ${labelDir}/*/${fd}/*.label
do
    pname=$(echo ${f} | awk -F "/" '{print $NF}' | cut -f1 -d ".") #get product name
    tname=$(echo ${f} | awk -F "/" '{print $(NF-2)}') #get task name
    for emb in ${embDir}/*/*/${fd}/*_${pname}.csv.${ptype}*
    do
        we=$(echo ${emb} | awk -F "/" '{print $(NF-3)}') #get embedding model 
        d=$(echo ${emb} | awk -F "/" '{print $(NF-2)}') #get embedding vector dimension 

        feaD=${fd}.${ptype}.fea
        labD=${fd}.${ptype}.lab
        rm ${labD}

        awk 'BEGIN{FS="[, ]";OFS=" "}{if(NR<=FNR){arr[$2]=1}else{if($1 in arr){print $0}}}' ${top10Dir}/${fd}/${pname}.closedBugs ${emb} > ${fd}.emb
        awk -v lab=${labD} 'BEGIN{FS="[ ,]"}{if(NR<=FNR){arr[$1]=$3}else{if($1 in arr){print arr[$1]>>lab;print $0}}}' ${f} ${fd}.emb | cut -f2- -d "," | sed 's/ $//' > ${feaD}.para
        echo ${f} ${emb}
        wc -l ${feaD}.para ${labD}
        ml="RF"
        echo ${feaD}.para ${labD} ${ml}
        datInfo=${fd},${pname},${ptype},${we},${d},${tname},${ml}
        echo ${datInfo}
        CUDA_VISIBLE_DEVICES=$cuda python para-emb-classification.py ${feaD}.para ${labD} ${ml} ${datInfo} ${resDir}/${fd}.${ptype}.emb.para
        #break
    done
    #break
done
