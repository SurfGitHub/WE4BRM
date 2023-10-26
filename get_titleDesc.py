import re
from lxml import etree
import sys
import os
import traceback
from text_preprocess import preprocess

def get_titleDesc(xml_fin, top10id_fin, bdata_fout, abBug_fout, fd):

    data = etree.iterparse(xml_fin, tag='item', huge_tree=True)
    br=[]
    bid=[]
    for b in top10id_fin.readlines():
        id=b.strip("\n").strip()
        if id != "bugId": bid.append(id)
    for _, elem in data:
        try:
            prod = elem.xpath('product/text()')[0]
            bugId = elem.xpath('id/text()')[0]
            if bugId in bid:
                if fd == "eclipse":
                    title = elem.xpath('summary/text()')[0]
                    desc = elem.xpath('description/text()')[0]
                elif fd == "mozilla":
                    title = elem.xpath('short_desc/text()')[0]
                    desc = elem.xpath('description/text()')[0]
                titleDesc=title.replace("\n"," ") + " " + desc.replace("\n"," ")
                titleDesc=preprocess(titleDesc)
                bdata=",".join([prod,bugId,titleDesc])
                br.append(bdata)
                if(len(br)==5000):
                    bdata_fout.write("\n".join(list(set(br)))+"\n")
                    br = []
        except:
            traceback.print_exc()
            abBug_fout.write('out of expected br:'+prod+" "+bugId+'\n')
    bdata_fout.write("\n".join(list(set(br)))+"\n")

if __name__ == '__main__':
    xml_fin = sys.argv[1] #original xml
    top10id_fin = sys.argv[2] #whose info need to be extracted
    b_fout = sys.argv[3] #store extracted title and desc of bugs from top10 products
    ab_fout =sys.argv[4] #record bugs that failed to be parsed
    fd = sys.argv[5] #which foundation's br xml. They differ slightly for specific fields
    get_titleDesc(xml_fin,open(top10id_fin,'r'),open(b_fout,'w'),open(ab_fout,'w'),fd)
