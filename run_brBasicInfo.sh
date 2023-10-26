#!/bin/bash
scriptDir=~/phd_gogogo/wordembedding
statDir=~/phd_gogogo/wordembedding/xml-stat-bak
xmlDir=~/phd_gogogo/wordembedding/xml-e-a-m
cd ${statDir}
python3 ${scriptDir}/get_brBasicInfo.py ${xmlDir}/apacheJiraAll.xml apache_brBasic apache.abNorbr apache
python3 ${scriptDir}/get_brBasicInfo.py ${xmlDir}/eclipse.xml  eclipse_brBasic eclipse.abNorbr eclipse
python3 ${scriptDir}/get_brBasicInfo.py ${xmlDir}/mozilla1.xml mozilla1_brBasic mozilla1.abNorbr mozilla
python3 ${scriptDir}/get_brBasicInfo.py ${xmlDir}/mozilla2.xml mozilla2_brBasic mozilla2.abNorbr mozilla
