#!/bin/bash
embDir="embVector"
labelDir="label"
top10Dir="top10"
resDir="embMLRes.para"
mkdir -p $resDir
emfd=$1 #eclipse or mozilla (em) foundation (emfd)

###Note that only for embs that gpu throws out of memory error, we would use this script to run the cpu version of emb-based rf para

while IFS=$"," read fd pname ptype we d tname ml splRatio feaRatio; #data format: eclipse,JDT,avg,bert,768,priority,RF,0.2,0.1
do
    f=${labelDir}/${tname}/${fd}/${pname}.label #label/fixingtime/eclipse/CDT.label
    emb=${embDir}/${we}/${d}/${fd}/*_${pname}.csv.${ptype}* #embVector/bert/768/eclipse/emb.modi.processed_CDT.csv.avgpooling
    feaD=${fd}.${ptype}.fea
    labD=${fd}.${ptype}.lab
    rm ${labD}

    awk 'BEGIN{FS="[, ]";OFS=" "}{if(NR<=FNR){arr[$2]=1}else{if($1 in arr){print $0}}}' ${top10Dir}/${fd}/${pname}.closedBugs ${emb} > ${fd}.emb
    awk -v lab=${labD} 'BEGIN{FS="[ ,]"}{if(NR<=FNR){arr[$1]=$3}else{if($1 in arr){print arr[$1]>>lab;print $0}}}' ${f} ${fd}.emb | cut -f2- -d "," | sed 's/ $//' > ${feaD}.para
    echo ${f} ${emb}
    wc -l ${feaD}.para ${labD}
    echo ${feaD}.para ${labD} ${ml}
    p_r_f=$(python para-cpu-emb-classification.py ${feaD}.para ${labD} ${splRatio} ${feaRatio})
    echo ${fd},${pname},${ptype},${we},${d},${tname},${ml},${splRatio},${feaRatio},${p_r_f} >> ${resDir}/${fd}.${ptype}.emb.para.cpu
    break
done < ${resDir}/${emfd}.missing.emb.para
