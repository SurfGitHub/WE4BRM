#!/bin/bash
pdir="afterPreprocess"
labelDir="label"
top10Dir="top10"
resDir="vsmMLRes.para"
mkdir -p $resDir
fd=$1
cuda=$2

#label data format:bugID,labelVal,label
for f in ${labelDir}/*/${fd}/*.label
do
    pname=$(echo ${f} | awk -F "/" '{print $NF}' | cut -f1 -d ".") #get product name
    tname=$(echo ${f} | awk -F "/" '{print $2}') #get task name
    for p in ${pdir}/${fd}/*_${pname}.csv
    do
        we="vsm"
        ptype="tfidf"
        d="allVoc"
        echo $f $p

        awk 'BEGIN{FS="[, ]";OFS=" "}{if(NR<=FNR){arr[$2]=1}else{if($1 in arr){print $0}}}' ${top10Dir}/${fd}/${pname}.closedBugs ${p} > ${fd}.vsmp
        awk 'BEGIN{FS="[, ]";OFS=" "}{if(NR<=FNR){arr[$1]=$3}else{if($1 in arr){print arr[$1],$0}}}' ${f} ${fd}.vsmp > ${fd}.vsmp.para
        for ml in "RF"
        do
            #echo $ml
            #p_r_f=$(CUDA_VISIBLE_DEVICES=$cuda python para-vsm-classification.py ${fd}.vsmp.para ${ml})
            ###p_r_f=$(python cpu-vsm-classification.py ${fd}.vsmp.para ${ml})
            #echo ${fd},${pname},${ptype},${we},${d},${tname},${ml},${p_r_f} >> ${resDir}/${fd}.${ptype}.ml.para

            ###the following is used to para tuning
            datInfo=${fd},${pname},${ptype},${we},${d},${tname},${ml}
            echo ${datInfo}
            CUDA_VISIBLE_DEVICES=$cuda python para-vsm-classification.py ${fd}.vsmp.para ${ml} ${datInfo} ${resDir}/${fd}.${ptype}.ml.para
            #echo ${fd},${pname},${ptype},${we},${d},${tname},${ml},${p_r_f} >> ${resDir}/${fd}.${ptype}.ml.para
            #break
        done
        #break
    done
    #break
done
