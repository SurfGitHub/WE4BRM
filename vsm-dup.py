import sys
import traceback
import cupy
import cudf
from cupyx.scipy.sparse import csr_matrix
from cuml.feature_extraction.text import TfidfVectorizer
from cuml.metrics import pairwise_distances
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

def vsm_pair_distance(br_fin,dup_group_dict,allB,dupRank_fout):
    corpus=[]
    brL=[]
    for br in br_fin.readlines():
        if(len(br.strip("\n").strip().split(" "))<2):continue
        bid, text = br.strip("\n").strip().split(" ",1)
        corpus.append(text)
        brL.append(int(bid))
    dat = cudf.DataFrame({'bid':brL,'text':corpus})
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(dat["text"]) #csr_matrix, sparse
    distM = pairwise_distances(X,metric="cosine")

    dupRank_fout.write("bid,dupid,rank,cosineSimiScore\n")
    for (k,v) in dup_group_dict.items():
        if len(v)<2: #each dup-master group should at least have 2 elements
            print('only 1 br:',k,dup_group_dict[k])
            continue
        for d in v[1:]: #the first br in v is the one with smallest bid, whose dups are not in previous brs, hence start with the second one
            earlier=[x for x in allB if x<d] #should only search dup in previous BRs
            try:
                dxIdx=brL.index(d)
                earlyIdx=[brL.index(x) for x in earlier]
            except:
                print('dxIdx or earlyIdx not in closed BRs:',dxIdx,earlyIdx)
                traceback.print_exc()
                continue

            dl=[(brL[i],float(distM[dxIdx,i])) for i in earlyIdx]
            dl=sorted(dl,key=lambda x: x[1])
            bl=[bid for (bid,cos) in dl]
            truDup=[x for x in v if x<d] #should only search dup in previous BRs
            for x in truDup:
            #note that: 1-dist is the cosine simi
                res=str(d)+","+ str(x) + "," + str(bl.index(x)) + "," + str(1-dl[bl.index(x)][1])
                dupRank_fout.write(res + "\n")

def do_dup_detection(br_fin,brText_fin,dupRes_fout):
    dupMgroups,dupBr,allBr = get_dupInfo(open(br_fin,'r'))
    vsm_pair_distance(open(brText_fin,'r'),dupMgroups,allBr,open(dupRes_fout,'w'))

if __name__ == '__main__':

    # example 1
    #test_list = [(1, 3), (4, 5)]
    #print(paired_elements_grouping(test_list))
    ## example 2
    #test_list = [(1, 3),(5,2), (4, 5),(7,4),(9,6)]
    #print(paired_elements_grouping(test_list))

    closedBr_fin = sys.argv[1] #format:closed bug files
    brText_fin = sys.argv[2] #br preprocessed text file
    dupRes_fout = sys.argv[3]
    do_dup_detection(closedBr_fin,brText_fin,dupRes_fout)
