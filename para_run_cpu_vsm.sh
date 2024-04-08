#!/bin/bash
pdir="afterPreprocess"
labelDir="label"
top10Dir="top10"
resDir="vsmMLRes.para"
mkdir -p $resDir
fd=$1

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
            datInfo=${fd},${pname},${ptype},${we},${d},${tname},${ml}
            echo ${datInfo}
            python para-cpu-rf-vsm.py ${fd}.vsmp.para ${datInfo} ${resDir}/${fd}.${ptype}.ml.para.cpu
            #break
        done
        #break
    done
    #break
done
