#!/bin/bash

glovePre=$1
words=$2
dim=$3

awk -v d=$dim '{
    if(NR<=FNR){
        emb[$1]=$0
    }
    else{
        for(idx=1;idx<=NF;idx++){
            if($idx~/[a-zA-Z]/){
                if ($idx in emb){
                    print emb[$idx]
                }
            }
            else {
                init="";
                for (i=1;i<=d;i++){
                    init=init" #"
                }
                print $idx""init
            }
        }
    }
}' ${glovePre} ${words}
