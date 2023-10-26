#!/bin/bash
missedF=$2 #some br may not have word embeddings [using max[i]=-100 to hint], i.e., no words can be found in pre-trained embeddings. In this case, record the their IDs.
cat $1 | awk -v mf=${missedF} 'BEGIN{bid=" ";avgp="";maxp="";FS=" ";OFS=","}{
    if($1~/[a-zA-Z]/){
            cnt++;
            for(i=2;i<=NF;i++){
                sum[i]+=$i;
                if($i>max[i]){
                    max[i]=$i
                }
            }
    }
    else{
        if(bid!=" "){
            if (max[2]!=-100) {
                for(i=2;i<=NF;i++){
                    avgp=avgp""sum[i]/cnt" "
                    maxp=maxp""max[i]" "
                }
                print bid,avgp,maxp
            }
            else {print bid >>mf}
        }
        avgp="";maxp="";
        bid=$1;cnt=0;
        for(i=2;i<=NF;i++){
            sum[i]=0;max[i]=-100
        }
    }
}
END{
    if (max[2]!=-100) {
        for(i=2;i<=NF;i++){
            avgp=avgp""sum[i]/cnt" "
            maxp=maxp""max[i]" "
        }
        print bid,avgp,maxp
    }
    else {print bid >>mf}
}'
