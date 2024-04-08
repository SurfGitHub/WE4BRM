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

def compareWE2VSM(embMLRes_fin,vsmMLRes_fin):

    t=pd.read_csv(embMLRes_fin,sep=",",header=None)
    t.columns=["fd","prod","ptype","we","dim","task","ml","sampRatio","feaRatio","p","r","f1"]
    t=t[(t["we"]!="ftBert_both") & (t["ml"]=="RF")]

    vsm_t=pd.read_csv(vsmMLRes_fin,sep=",",header=None) #all vsm ml results are RF based results on vsm-tfidf features
    vsm_t.columns=["fd","prod","ptype","we","dim","task","ml","sampRatio","feaRatio","p","r","f1"]
    for ta in ['fixingtime','severity','priority','reopen','reassignment']:
        tt=t[t["task"]==ta]

        vsm=vsm_t["f1"][vsm_t["task"]==ta]
        bert=tt["f1"][tt["we"]=="bert"]
        elmo=tt["f1"][tt["we"]=="elmo"]
        f300=tt["f1"][(tt["we"]=="fastText") & (tt["dim"]==300)]
        g300=tt["f1"][(tt["we"]=="glove") & (tt["dim"]==300)]
        word2vec=tt["f1"][(tt["we"]=="word2vec") & (tt["dim"]==300)]

        data=np.array([vsm,bert,elmo,f300,g300,word2vec])
        print('rq3-we2vsm-Friedman-test-'+ta+':',friedmanchisquare(vsm,bert,elmo,f300,g300,word2vec))

        ranks = np.argsort(-data, axis=0) + 1
        mean_ranks = np.sum(ranks, axis=1) /len(bert)

        cd = Orange.evaluation.compute_CD(mean_ranks, len(bert),test='bonferroni-dunn')
        methods=[('vsm','tfidf'),('bert',768),('elmo',1024),('fastText',300),('glove',300),('word2vec',300)]

        cd_fout='rq3-we2vsm-'+ta+'.pdf'
        pp=PdfPages(cd_fout)
        cdplot=Orange.evaluation.graph_ranks(mean_ranks, methods, cd=cd, cdmethod=0, width=6, textspace=1.5)
        pp.savefig(cdplot)
        pp.close()
        comp_list=[('bert',768),('elmo',1024),('fastText',300),('glove',300),('word2vec',300)]
        for (i,j) in comp_list:
            idat=tt["f1"][(tt["we"]==i) & (tt["dim"]==j)]
            wd,wdres = wilcoxon(idat,vsm)
            print(ta,'wilcoxon:',wd,wdres)
            d, res = cliffs_delta(idat, vsm)
            print(ta,(i,j),'vsm',d,res)

def compareBertFT(embMLRes_fin):

    t=pd.read_csv(embMLRes_fin,sep=",",header=None)
    t.columns=["fd","prod","ptype","we","dim","task","ml","sampRatio","feaRatio","p","r","f1"]
    bert_t  =t[t["we"]=="bert"]
    ftbert_t=t[t["we"]=="ftBert_both"]
    for ta in ['fixingtime','severity','priority','reopen','reassignment']:
        print(ta)
        bert=bert_t["f1"][bert_t["task"]==ta]
        ftbert=ftbert_t["f1"][ftbert_t["task"]==ta]
        wd,wdres = wilcoxon(bert,ftbert)
        print(ta,'wilcoxon:',wd,wdres)
        d, res = cliffs_delta(bert, ftbert)
        print(ta,'bert','ftbert',d,res)

if __name__ == '__main__':
    embMLFin = sys.argv[1]
    vsmMLFin = sys.argv[2]
    compareWE2VSM(embMLFin,vsmMLFin)
    compareBertFT(embMLFin)
