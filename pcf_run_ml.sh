#!/bin/bash
embDir="embVector"
labelDir="label"
resDir="embMLRes"
pcfDir="p-c-f-closed"
mkdir -p $resDir
fd=$1
cuda=$2
ptype=$3 # max or avg pooling
#f format:bugID,keyID,label,labelOriValue(if exists), we use keyId in emb dat files
for f in ${labelDir}/*/${fd}/*.label
do
    pname=$(echo ${f} | awk -F "/" '{print $NF}' | cut -f1 -d ".") #get product name
    tname=$(echo ${f} | awk -F "/" '{print $2}') #get task name
    if [[ $pname == "Core" ]] || [[ $pname == "Firefox" ]] || [[ $pname == "Platform" ]];then
        echo $pname": 5w version of p-c-f now"

        awk -F "," '{if(NR<=FNR){arr[$2]=1}else{if($1 in arr){print $0}}}' ${pcfDir}/${pname}.5w.closedBugs ${f} > ${pname}.5wL
        for emb in ${embDir}/*/*/${fd}/*_${pname}.csv.${ptype}*
        do
            we=$(echo ${emb} | awk -F "/" '{print $2}') #get embedding model 
            d=$(echo ${emb} | awk -F "/" '{print $3}') #get embedding vector dimension 
    
            feaD=${fd}.${ptype}.fea
            labD=${fd}.${ptype}.lab
            rm ${labD}
            awk -v lab=${labD} 'BEGIN{FS="[ ,]"}{if(NR<=FNR){arr[$1]=$3}else{if($1 in arr){print arr[$1]>>lab;print $0}}}' ${pname}.5wL ${emb} | cut -f2- -d "," | sed 's/ $//' > ${feaD}
            echo ${f} ${emb}
            wc -l ${feaD} ${labD}
            for ml in "Logistic" "SVM" "RF" "NB"
            do
    
                echo ${feaD} ${labD} ${ml}
                p_r_f=$(CUDA_VISIBLE_DEVICES=$cuda python br-cuml.py $feaD $labD $ml)
                echo ${fd},${pname},${ptype},${we},${d},${tname},${ml},${p_r_f} >> ${resDir}/${fd}.${ptype}.ml.5w
                #break
            done
            #break
        done
        #break
    fi
done
