#!/bin/bash

function get_top10closedbugs(){
    #top10 products from eclipse with largest br cnt:head eclipse.brCnt | cut -f1 -d "," | tr -s '\n' ' '
    E="eclipse"
    res=top10/${E}
    mkdir -p ${res}/
    for p in "Platform" "z_Archived" "JDT" "Community" "CDT" "PDE" "Equinox" "Papyrus" "Orion" "Mylyn"
    do
        python3 ./get_top10prod_closedbugs.py ${E}_brBasic ${E} ${p} ${res}/${p}.closedBugs 
    done
    
    #top10 products from mozilla with largest br cnt:head mozilla.brCnt | cut -f1 -d "," | tr -s '\n' ' '
    M="mozilla"
    res=top10/${M}
    mkdir -p ${res}/
    for p in "Core" "Firefox" "SeaMonkey" "Firefox OS Graveyard" "Thunderbird" "Toolkit" "Firefox for Android Graveyard" "DevTools" "Testing" "MailNews Core"
    do
        python3 ./get_top10prod_closedbugs.py ${M}_brBasic ${M} "$p" "${res}/${p}.closedBugs"
    done
}
#get_top10closedbugs

function ft_pri_sev_label(){
    for fd in "eclipse" "mozilla"
    do
        fixtlab=label/fixingtime/
        mkdir -p ${fixtlab}/${fd}
        priolab=label/priority
        mkdir -p ${priolab}/${fd}
        sevelab=label/severity
        mkdir -p ${sevelab}/${fd}
    done

    E="eclipse"
    for p in "Platform" "z_Archived" "JDT" "Community" "CDT" "PDE" "Equinox" "Papyrus" "Orion" "Mylyn"
    do
        #fixing time label
        awk 'BEGIN{FS=",";OFS=","}{if($4=="FIXED"){if($8<=5){lab=0}if($8>5 && $8<=10){lab=1}if($8>10){lab=2}print $2,$8,lab}}' top10/${E}/${p}.closedBugs > ${fixtlab}/${E}/${p}.label

        #priority label
        awk 'BEGIN{FS=",";OFS=","}{if($3!="REOPENED"){lab=" ";if($5=="P1" || $5=="P2"){lab=0}if($5=="P3"){lab=1}if($5=="P4" || $5=="P5"){lab=2}if(lab!=" "){print $2,$5,lab}}}' top10/${E}/${p}.closedBugs > ${priolab}/${E}/${p}.label

        #severity label:blocker critical enhancement major minor normal trivial
        awk 'BEGIN{FS=",";OFS=","}{if($3!="REOPENED"){lab=" ";if($6=="blocker" || $6=="critical" || $6=="major"){lab=0}if($6=="minor" || $6=="trivial"){lab=1}if(lab!=" "){print $2,$6,lab}}}' top10/${E}/${p}.closedBugs > ${sevelab}/${E}/${p}.label
    done

    #####################To label Mozilla, mozilla severity levels is more complex than eclipse. 
    #Mozilla has more default--values for priority and severity.#####################
    M="mozilla"
    for p in "Core" "Firefox" "SeaMonkey" "Firefox-OS-Graveyard" "Thunderbird" "Toolkit" "Firefox-for-Android-Graveyard" "DevTools" "Testing" "MailNews-Core"
    do
        #fixing time label
        awk 'BEGIN{FS=",";OFS=","}{if($4=="FIXED"){if($8<=5){lab=0}if($8>5 && $8<=10){lab=1}if($8>10){lab=2}print $2,$8,lab}}' top10/${M}/${p}.closedBugs > ${fixtlab}/${M}/${p}.label

        #priority label
        awk 'BEGIN{FS=",";OFS=","}{if($3!="REOPENED"){lab=" ";if($5=="P1" || $5=="P2"){lab=0}if($5=="P3"){lab=1}if($5=="P4" || $5=="P5"){lab=2}if(lab!=" "){print $2,$5,lab}}}' top10/${M}/${p}.closedBugs > ${priolab}/${M}/${p}.label

        #severity label:blocker critical enhancement major minor normal seve trivial and S1-S4,N/A (https://wiki.mozilla.org/BMO/UserGuide/BugFields#bug_severity)
        awk 'BEGIN{FS=",";OFS=","}{if($3!="REOPENED"){lab=" ";if($6=="S1" || $6=="S2" || $6=="blocker" || $6=="critical" || $6=="major"){lab=0}if($6=="S4" || $6=="minor" || $6=="trivial"){lab=1}if(lab!=" "){print $2,$6,lab}}}' top10/${M}/${p}.closedBugs > ${sevelab}/${M}/${p}.label
    done
}
#ft_pri_sev_label

function reopen_reass_label(){
    reopenAssDir="./reassignment_reopen"
    for fd in "eclipse" "mozilla"
    do
        reopenlab=label/reopen
        mkdir -p ${reopenlab}/${fd}
        reasslab=label/reassignment
        mkdir -p ${reasslab}/${fd}
    done

    #E="eclipse"
    #for p in "Platform" "z_Archived" "JDT" "Community" "CDT" "PDE" "Equinox" "Papyrus" "Orion" "Mylyn"
    #do
    #    #reopen label: eclipse/mozilla_reopen.csv format:bug_id, is_reopened, is_reopen_not_closed
    #    awk 'BEGIN{FS=",";OFS=","}{if(NR<=FNR){arr[$1]=$2;brr[$1]=$3}else{if($2 in arr){print $2,brr[$2],arr[$2]}}}' ${reopenAssDir}/${E}_reopen.csv top10/${E}/${p}.closedBugs > ${reopenlab}/${E}/${p}.label

    #    #reass label:eclipse/mozilla_reassignment.csv format:bug_id, sixReassItems, is_reass, is_reopen_not_closed
    #    #awk 'BEGIN{FS=",";OFS=","}{if(NR<=FNR){if($9==0){arr[$1]=$8;brr[$1]=$9}}else{if($2 in arr){print $2,brr[$2],arr[$2]}}}' ${reopenAssDir}/${E}_reassignment.csv top10/${E}/${p}.closedBugs > ${reasslab}/${E}/${p}.label
    #    awk 'BEGIN{FS=",";OFS=","}{if(NR<=FNR){arr[$1]=$8;brr[$1]=$9}else{if(($2 in arr)&&($3!="REOPENED")){print $2,brr[$2],arr[$2]}}}' ${reopenAssDir}/${E}_reassignment.csv top10/${E}/${p}.closedBugs > ${reasslab}/${E}/${p}.label
    #done

    #####################To label Mozilla as the same way for eclipse
    M="mozilla"
    for p in "Core" "Firefox" "SeaMonkey" "Firefox-OS-Graveyard" "Thunderbird" "Toolkit" "Firefox-for-Android-Graveyard" "DevTools" "Testing" "MailNews-Core"
    do
        #reopen label: eclipse/mozilla_reopen.csv format:bug_id, is_reopened, is_reopen_not_closed
        awk 'BEGIN{FS=",";OFS=","}{if(NR<=FNR){arr[$1]=$2;brr[$1]=$3}else{if($2 in arr){print $2,brr[$2],arr[$2]}}}' ${reopenAssDir}/${M}_reopen.csv top10/${M}/${p}.closedBugs > ${reopenlab}/${M}/${p}.label

        #reass label:eclipse/mozilla_reassignment.csv format:bug_id, sixReassItems, is_reass, is_reopen_not_closed
        awk 'BEGIN{FS=",";OFS=","}{if(NR<=FNR){arr[$1]=$8;brr[$1]=$9}else{if(($2 in arr)&&($3!="REOPENED")){print $2,brr[$2],arr[$2]}}}' ${reopenAssDir}/${M}_reassignment.csv top10/${M}/${p}.closedBugs > ${reasslab}/${M}/${p}.label
    done
}
reopen_reass_label
