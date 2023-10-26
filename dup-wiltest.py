import sys
import os
import scipy.stats
from scipy.stats import friedmanchisquare
from scipy.stats import wilcoxon
import Orange
from Orange.evaluation import compute_CD, graph_ranks
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np
from numpy import std, mean, sqrt
from itertools import combinations
import scikit_posthocs as sp
from cliffs_delta import cliffs_delta

def compareWE(embDupRes_fin,pType):

    #header:fd,prod,ptype,we,dim,totalBR,20RankCnts,20Recalls
    t=pd.read_csv(embDupRes_fin,sep=",",header=0)

    t=t[t["we"]!="ftBert_both"]
    #pp=PdfPages(cd_fout)
    for r in ['recall_1','recall_5','recall_10','recall_15','recall_20']:
        #tt=t[(t["ptype"]=="avg") & (t["fd"]=="eclipse")]
        tt=t[(t["ptype"]==pType)]

        bert=tt[r][tt["we"]=="bert"]
        elmo=tt[r][tt["we"]=="elmo"]
        #f100=tt[r][(tt["we"]=="fastText") & (tt["dim"]==100)]
        #f200=tt[r][(tt["we"]=="fastText") & (tt["dim"]==200)]
        f300=tt[r][(tt["we"]=="fastText") & (tt["dim"]==300)]
        #g50=tt[r][(tt["we"]=="glove") & (tt["dim"]==50)]
        #g100=tt[r][(tt["we"]=="glove") & (tt["dim"]==100)]
        #g200=tt[r][(tt["we"]=="glove") & (tt["dim"]==200)]
        g300=tt[r][(tt["we"]=="glove") & (tt["dim"]==300)]
        word2vec=tt[r][(tt["we"]=="word2vec") & (tt["dim"]==300)]

        print(len(bert),len(word2vec))
        #data=np.array([bert,elmo,f100,f200,f300,g50,g100,g200,g300,word2vec])
        #print(friedmanchisquare(bert,elmo,f100,f200,f300,g50,g100,g200,g300,word2vec))
        data=np.array([bert,elmo,f300,g300,word2vec])
        print('rq2-we-dup-'+r+'-friedman-test:',friedmanchisquare(bert,elmo,f300,g300,word2vec))
        #print(sp.posthoc_nemenyi_friedman(data.T))

        ranks = np.argsort(-data, axis=0) + 1
        mean_ranks = np.sum(ranks, axis=1) /len(bert)
        print('mean_ranks:',mean_ranks)
        cd = Orange.evaluation.compute_CD(mean_ranks, len(bert))
        print("cd:",cd)

        #methods=[('bert',768),('elmo',1024),('fastText',100),('fastText',200),('fastText',300),('glove',50),('glove',100),('glove',200),('glove',300),('word2vec',300)]

        cd_fout='rq2-we-dup-'+r+'.pdf'
        pp = PdfPages(cd_fout)
        methods=[('bert',768),('elmo',1024),('fastText',300),('glove',300),('word2vec',300)]
        cdplot=Orange.evaluation.graph_ranks(mean_ranks, methods, cd=cd, width=6, textspace=1.5)
        pp.savefig(cdplot)
        pp.close()

        comp_list=[('bert',768),('elmo',1024),('fastText',300),('glove',300),('word2vec',300)]
        combs = np.fromiter(combinations(range(len(comp_list)),2), dtype='i,i')
        for (i,j) in combs:
            (w1,d1) = comp_list[i]
            (w2,d2) = comp_list[j]
            idat=tt[r][(tt["we"]==w1) & (tt["dim"]==d1)]
            jdat=tt[r][(tt["we"]==w2) & (tt["dim"]==d2)]

            #wd,wdres = wilcoxon(idat,jdat)
            #print(r,'wilcoxon:',wd,wdres)
            d, res = cliffs_delta(idat, jdat)
            print(r,comp_list[i],comp_list[j],d,res)
    #pp.close()

def compareWE2VSM(embDupRes_fin,vsmDupRes_fin,pType):

    t=pd.read_csv(embDupRes_fin,sep=",",header=0)
    t=t[t["we"]!="ftBert_both"]

    vsm_t=pd.read_csv(vsmDupRes_fin,sep=",",header=0)
    for r in ['recall_1','recall_5','recall_10','recall_15','recall_20']:
        tt=t[(t["ptype"]==pType)]
    #pp=PdfPages(cd_fout)

        vsm=vsm_t[r]
        bert=tt[r][tt["we"]=="bert"]
        elmo=tt[r][tt["we"]=="elmo"]
        #f100=tt[r][(tt["we"]=="fastText") & (tt["dim"]==100)]
        #f200=tt[r][(tt["we"]=="fastText") & (tt["dim"]==200)]
        f300=tt[r][(tt["we"]=="fastText") & (tt["dim"]==300)]
        #g50=tt[r][(tt["we"]=="glove") & (tt["dim"]==50)]
        #g100=tt[r][(tt["we"]=="glove") & (tt["dim"]==100)]
        #g200=tt[r][(tt["we"]=="glove") & (tt["dim"]==200)]
        g300=tt[r][(tt["we"]=="glove") & (tt["dim"]==300)]
        word2vec=tt[r][(tt["we"]=="word2vec") & (tt["dim"]==300)]

        #data=np.array([vsm,bert,elmo,f100,f200,f300,g50,g100,g200,g300,word2vec])
        #print(friedmanchisquare(bert,elmo,f100,f200,f300,g50,g100,g200,g300,word2vec))

        data=np.array([vsm,bert,elmo,f300,g300,word2vec])
        print('rq3-we2vsm-friedman-test-'+r+':',friedmanchisquare(vsm,bert,elmo,f300,g300,word2vec))
        #print(sp.posthoc_nemenyi_friedman(data.T))

        ranks = np.argsort(-data, axis=0) + 1
        mean_ranks = np.sum(ranks, axis=1) /len(bert)
        print('mean_ranks:',mean_ranks)
        cd = Orange.evaluation.compute_CD(mean_ranks, len(bert),test='bonferroni-dunn')
        print("cd:",cd)

        #methods=[('vsm','tfidf'),('bert',768),('elmo',1024),('fastText',100),('fastText',200),('fastText',300),('glove',50),('glove',100),('glove',200),('glove',300),('word2vec',300)]

        cd_fout='rq3-we2vsm-dup-'+r+'.pdf'
        pp=PdfPages(cd_fout)
        methods=[('vsm','tfidf'),('bert',768),('elmo',1024),('fastText',300),('glove',300),('word2vec',300)]
        cdplot=Orange.evaluation.graph_ranks(mean_ranks, methods, cd=cd, cdmethod=0, width=6, textspace=1.5)
        pp.savefig(cdplot)
        pp.close()

        #comp_list=[('bert',768),('elmo',1024),('fastText',100),('fastText',200),('fastText',300),('glove',50),('glove',100),('glove',200),('glove',300),('word2vec',300)]
        comp_list=[('bert',768),('elmo',1024),('fastText',300),('glove',300),('word2vec',300)]
        for (i,j) in comp_list:
            idat=tt[r][(tt["we"]==i) & (tt["dim"]==j)]

            #wd,wdres = wilcoxon(idat,vsm)
            #print(r,'wilcoxon:',wd,wdres)
            d, res = cliffs_delta(idat, vsm)
            print(r,(i,j),'vsm',d,res)
    #pp.close()


def compareBertFT(embDupRes_fin,pType):

    t=pd.read_csv(embDupRes_fin,sep=",",header=0)
    t=t[(t["ptype"]==pType)]
    bert_t  =t[t["we"]=="bert"]
    ftbert_t=t[t["we"]=="ftBert_both"]
    for r in ['recall_1','recall_5','recall_10','recall_15','recall_20']:
        bert=bert_t[r]
        ftbert=ftbert_t[r]
        wd,wdres = wilcoxon(bert,ftbert)
        print(r,'wilcoxon:',wd,wdres)
        d, res = cliffs_delta(bert, ftbert)
        print(r,'bert','ftbert',d,res)

def compareDim(embDupRes_fin,pType,comp_list):

    #header:fd,prod,ptype,we,dim,totalBR,20RankCnts,20Recalls
    t=pd.read_csv(embDupRes_fin,sep=",",header=0)
    t=t[(t["we"]!="ftBert_both") & (t["ptype"]==pType)]
    for r in ['recall_1','recall_5','recall_10','recall_15','recall_20']:
        vl=[]
        print(comp_list)
        for (i,j) in comp_list:
            print(i,j)
            v=t[r][(t["we"]==i) & (t["dim"]==j)]
            vl.append(np.array(v))
            print(len(v),v)

        data=np.array(vl)
        print('rq2-dimsize-dup-'+r+'-friedman-test-'+comp_list[0][0]+':',friedmanchisquare(*data))
        #print(sp.posthoc_nemenyi_friedman(data.T))

        ranks = np.argsort(-data, axis=0) + 1
        mean_ranks = np.sum(ranks, axis=1) /len(vl[0])
        print('mean_ranks:',mean_ranks)
        cd = Orange.evaluation.compute_CD(mean_ranks, len(vl[0]))
        print("cd:",cd)

        #methods=[('fastText',100),('fastText',200),('fastText',300)]

        cd_fout='rq2-dimsize-dup-'+r+'-'+comp_list[0][0]+'.pdf'
        pp = PdfPages(cd_fout)
        cdplot=Orange.evaluation.graph_ranks(mean_ranks, comp_list, cd=cd, width=6, textspace=1.5)
        pp.savefig(cdplot)
        pp.close()

        #comp_list=[('fastText',100),('fastText',200),('fastText',300)]
        combs = np.fromiter(combinations(range(len(comp_list)),2), dtype='i,i')
        for (i,j) in combs:
            (w1,d1) = comp_list[i]
            (w2,d2) = comp_list[j]
            idat=t[r][(t["we"]==w1) & (t["dim"]==d1)]
            jdat=t[r][(t["we"]==w2) & (t["dim"]==d2)]
            d, res = cliffs_delta(idat, jdat)
            print(r,comp_list[i],comp_list[j],d,res)
    #pp.close()
if __name__ == '__main__':
    embDupFin = sys.argv[1] #dup res
    vsmDupFin = sys.argv[2]
    #cdFout = sys.argv[3]
    pType = sys.argv[3] #avg or max pooling

    #pp = PdfPages(cdFout)

    comp_list=[('fastText',100),('fastText',200),('fastText',300)]
    compareDim(embDupFin,pType,comp_list)

    comp_list=[('glove',50),('glove',100),('glove',200),('glove',300)]
    compareDim(embDupFin,pType,comp_list)
    compareWE(embDupFin,pType)
    compareWE2VSM(embDupFin,vsmDupFin,pType)
    compareBertFT(embDupFin,pType)
    #pp.close()
