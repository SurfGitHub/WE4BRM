import re
from lxml import etree
from datetime import datetime
import sys
import os
import traceback
def get_brBasicInfo(xml_fin, bdata_fout, abBug_fout, fd):

    data = etree.iterparse(xml_fin, tag='item', huge_tree=True)

    if fd == "eclipse" or fd == "mozilla": #eclipse and mozilla bugzilla
        header="prod,bugId,status,reso,prio,seve,dupid,fTime,cTime,dTime"
    if fd == "apache": #apache jira, no severity but added type field
        header="prod,bugId,status,reso,prio,type,dupid,fTime,cTime,dTime"
    bdata_fout.write(header+'\n')
    br=[]

    for _, elem in data:
        try:
            #the following 5 fields using the same tag names for eclipse/mozilla bugzilla and apache jira
            prod = elem.xpath('product/text()')[0]
            bugId = elem.xpath('id/text()')[0]
            prio = elem.xpath('priority/text()')[0]
            dupid = elem.xpath('dup_id/text()')[0]
            reso = elem.xpath('resolution/text()')[0]

            if fd == "apache":
                status = reso #we mix reso and status together while dowloanding brs for apache
                #Jira explicitly use this field to indicate a bug or others, eclipse/mozlla do not have
                typ = elem.xpath('type/text()')[0]
            else:
                status = elem.xpath('bug_status/text()')[0]
                seve = elem.xpath('bug_severity/text()')[0] #only eclipse and mozilla have severity item

            #different tag names for the same reporting and closing time of a bug report
            if fd == "apache":
                cTime = elem.xpath('create_ts/text()')[0]
                dTime = elem.xpath('delta_ts/text()')[0]
            elif fd == "eclipse":
                cTime = elem.xpath('create_time/text()')[0]
                dTime = elem.xpath('delta_time/text()')[0]
            elif fd == "mozilla":
                cTime = elem.xpath('creation_ts/text()')[0]
                dTime = elem.xpath('delta_ts/text()')[0]
            #fixing time in days
            if fd == "apache":
                fTime = (datetime.strptime(dTime,'%a, %d %b %Y %H:%M:%S %z') -
                    datetime.strptime(cTime, '%a, %d %b %Y %H:%M:%S %z')).total_seconds()/(3600*24)
            elif fd == "eclipse" or fd == "mozilla":
                fTime = (datetime.strptime(dTime,'%Y-%m-%d %H:%M:%S %z') -
                    datetime.strptime(cTime, '%Y-%m-%d %H:%M:%S %z')).total_seconds()/(3600*24)

            if fd == "eclipse" or fd == "mozilla":
                brInfo=[prod,bugId,status,reso,prio,seve,dupid,str(fTime),cTime,dTime]
            elif fd == "apache":
                brInfo=[prod,bugId,status,reso,prio,typ,dupid,str(fTime),cTime,dTime]
            bdata=",".join(brInfo)
            br.append(bdata)
            #bdata_fout.write(bdata+'\n')
        except:
            traceback.print_exc()
            abBug_fout.write('out of expected br:'+prod+" "+bugId+'\n')
    bdata_fout.write("\n".join(list(set(br)))+"\n")

if __name__ == '__main__':
    xml_fin = sys.argv[1] #original xml
    b_fout = sys.argv[2] #store extracted bugs with all needed items
    ab_fout =sys.argv[3] #record bugs that failed to be parsed
    fd = sys.argv[4] #which foundation's br xml. They differ slightly for specific fields
    get_brBasicInfo(xml_fin,open(b_fout,'w'),open(ab_fout,'w'),fd)
