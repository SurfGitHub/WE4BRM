import re
from datetime import datetime
import sys
import os
import traceback
import pandas as pd

#br_fin format: prod,bugId,status,reso,prio,seve,dupid,fTime,cTime,dTime
def get_closedBugs(br_fin,fd,prod,closed_fout):
    t = pd.read_csv(br_fin)
    if fd == "eclipse" or fd == "mozilla":
        cond = (t['prod']== prod) & ((t['status'] == "RESOLVED") | (t['status'] == "CLOSED") | (t['status'] == "VERIFIED") | (t['status'] == "REOPENED"))
    elif fd == "apache": #need to verify for apache...
        cond = (t['prod']== prod) & (t['type'] == "Bug") & ((t['status'] == "RESOLVED") | (t['status'] == "CLOSED") | (t['status'] == "VERIFIED") | (t['reso'] == "FIXED")) #adding fixed reso incase missing other status value

    t = t[cond].to_csv(closed_fout,index=False)
if __name__ == '__main__':
    br_fin = sys.argv[1] #original brBasic info file
    fd = sys.argv[2] #which foundation
    prod =sys.argv[3] #which product
    closed_fout = sys.argv[4] #the basic info of bugs from top 10 products of a specific foundation
    get_closedBugs(br_fin,fd,prod,open(closed_fout,'w'))
