import sys
import time
from datetime import datetime
import traceback
import pandas as pd
from sklearn.metrics import pairwise_distances
import networkx as nx
import itertools

#group pairs based on common items, used to group dup-master pairs in this case
def paired_elements_grouping(L):
    G=nx.from_edgelist(L)
    l=list(nx.connected_components(G))
    mapdict={z:x for x, y in enumerate(l) for z in y }
    newlist=[ x+(mapdict[x[0]],)for  x in L]
    newlist=sorted(newlist,key=lambda x : x[2])
    yourlist=[list(y) for x , y in itertools.groupby(newlist,key=lambda x : x[2])]
    gd={}
    for i in yourlist:
        for (x,y,z) in i:
            if z not in gd: gd[z]=set()
            gd[z].add(x)
            gd[z].add(y)
    return gd

#top10 closed file:prod,bugId,status,reso,prio,seve,dupid,fTime,cTime,dTime
#dupBr is used to group dup-master groups based on the top10 closed file
#the obtained allB,dupB, and dupBrGroups would be used to cal cosine simi for dup detection
def get_dupInfo(closedBR_fin):
    allB=[]
    dupB=[]
    dupMaster=[]
    dupBrGroups={}
    for br in closedBR_fin.readlines():
        try:
            fields = br.strip("\n").strip().split(",")
        except:
            traceback.print_exc()
            continue
        if fields[1] == "bugId": continue #the first header line
        bid = int(fields[1])
        allB.append(bid)

        dupid = fields[6]
        if dupid != "None":
            dupB.append(bid)
            dupMaster.append((bid,int(dupid)))

    groups=paired_elements_grouping(dupMaster)
    for gid,gmem in groups.items():
        valid=gmem.intersection(set(allB))
        if len(valid)>1: dupBrGroups[gid]=sorted(valid)
    return dupBrGroups,dupB,allB

def emb_pair_distance(emb_fin,dup_group_dict,allB,dupRank_fout):
    allEmb = pd.read_csv(emb_fin,sep="[ ,]", header=None, engine='python')
    cname=["f"+str(i) for i in range(1,len(allEmb.columns))]
    cname.insert(0,'bid')
    allEmb.columns = cname
    allEmb["bid"].astype(int)
    distM = pairwise_distances(allEmb.drop(columns=['bid']), metric="cosine")
    #print("allEmbBid:",allEmb['bid'])

    dupRank_fout.write("bid,dupid,rank,cosineSimiScore\n")
    print("total dup-master groups:",len(dup_group_dict))
    for (k,v) in dup_group_dict.items():
        #print(v)
        if len(v)<2: #each dup-master group should at least have 2 elements
            print("only 1 br:",k,dup_group_dict[k])
            continue
        cosD = {}
        #the first br in v is the one with smallest bid, whose dups are not in previous brs,
        #hence start with the second one
        for d in v[1:]:
            #print("dupid:",d)
            earlier=[x for x in allB if x<d] #should only search dup in previous BRs
            #print("earlier:",earlier)
            dxIdx=allEmb.loc[allEmb['bid']==d].index.tolist()
            earlyIdx=allEmb.loc[allEmb['bid'].isin(earlier)].index.tolist()
            #print(dxIdx,earlyIdx)
            if len(dxIdx)==0 or len(earlyIdx)==0:
                print('dxIdx or earlyIdx not in allEmb:',dxIdx,earlyIdx)
                continue

            for i in earlyIdx:
                cosD[allEmb['bid'][i]]=float(distM[dxIdx,i])
                #print(i,dxIdx,allEmb['bid'][i],float(distM[dxIdx,i]))
            dl=[(allEmb['bid'][i],float(distM[dxIdx,i])) for i in earlyIdx]
            dl=sorted(dl,key=lambda x: x[1]) #sort by distance in ascend order!! smaller dist indicates more similar
            bl=[bid for (bid,cos) in dl]
            #print(dl,bl)
            truDup=[x for x in v if x<d] #should only consider the ranks of previous BRs of d
            #print(truDup)
            for x in truDup:
            #note that: 1-dist is the cosine simi
                res=str(d)+","+ str(x) + "," + str(bl.index(x)) + "," + str(1-dl[bl.index(x)][1])
                dupRank_fout.write(res + "\n")
            #print([(d,x,bl.index(x),dl[bl.index(x)][1]) for x in truDup])

def do_dup_detection(br_fin,emb_fin,dupRes_fout):
    dupMgroups,dupBr,allBr = get_dupInfo(open(br_fin,'r'))
    #print(dupMgroups,dupBr,allBr)
    emb_pair_distance(open(emb_fin,'r'),dupMgroups,allBr,open(dupRes_fout,'w'))

if __name__ == '__main__':
    #top10 closed file:prod,bugId,status,reso,prio,seve,dupid,fTime,cTime,dTime
    br_fin = sys.argv[1]
    #embedding vector file:bid, f1 f2 ... fn
    emb_fin = sys.argv[2]
    dupRes_fout = sys.argv[3]
    do_dup_detection(br_fin,emb_fin,dupRes_fout)
