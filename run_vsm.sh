#!/bin/bash
pdir="afterPreprocess"
labelDir="label"
resDir="vsmMLRes"
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
        awk 'BEGIN{FS="[, ]";OFS=" "}{if(NR<=FNR){arr[$1]=$3}else{if($1 in arr){print arr[$1],$0}}}' ${f} ${p} > ${fd}.vsmp
        for ml in "Logistic" "SVM" "RF" "NB"
        do
            echo $ml
            p_r_f=$(CUDA_VISIBLE_DEVICES=$cuda python vsm-classification.py ${fd}.vsmp ${ml})
            #p_r_f=$(python cpu-vsm-classification.py ${fd}.vsmp ${ml})
            echo ${fd},${pname},${ptype},${we},${d},${tname},${ml},${p_r_f} >> ${resDir}/${fd}.${ptype}.ml
            #break
        done
        #break
    done
    #break
done
