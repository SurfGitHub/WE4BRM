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

def compareML(embMLRes_fin):
    t=pd.read_csv(embMLRes_fin,sep=",",header=None)
    t.columns=["fd","prod","ptype","we","dim","task","ml","p","r","f1"]
    t=t[(t["we"]!="ftBert_both")]
    for ta in ['fixingtime','severity','priority','reopen','reassignment']:
        tt=t[t["task"]==ta]

        svm=tt["f1"][tt["ml"]=="SVM"]
        rf=tt["f1"][tt["ml"]=="RF"]
        lg=tt["f1"][tt["ml"]=="Logistic"]
        nb=tt["f1"][tt["ml"]=="NB"]
        print(ta+'-rq1-ml-Friedman-test:',friedmanchisquare(rf, svm, lg, nb))
        data = np.array([rf, svm, lg, nb])
        #print(sp.posthoc_nemenyi_friedman(data.T))

        ranks = np.argsort(-data, axis=0) + 1
        mean_ranks = np.sum(ranks, axis=1) /len(rf)
        cd = Orange.evaluation.compute_CD(mean_ranks, len(rf))
        #print("cd:",cd)

        methods=['RF','SVM','Logistic','NB']

        cd_fout='rq1-ml-'+ta+'.pdf'
        pp = PdfPages(cd_fout)
        cdplot=Orange.evaluation.graph_ranks(mean_ranks, methods, cd=cd, width=6, textspace=1.5)
        pp.savefig(cdplot)
        pp.close()

        #pairwise comparision between ML algorithms
        comp_list=['RF','SVM','Logistic','NB']
        combs = np.fromiter(combinations(range(len(comp_list)),2), dtype='i,i')
        for (i,j) in combs:
            idat=tt["f1"][tt["ml"]==comp_list[i]]
            jdat=tt["f1"][tt["ml"]==comp_list[j]]
            d, res = cliffs_delta(idat, jdat)
            print(comp_list[i],comp_list[j],d,res)

    #pp.close()

def compareWE(embMLRes_fin):

    t=pd.read_csv(embMLRes_fin,sep=",",header=None)
    t.columns=["fd","prod","ptype","we","dim","task","ml","p","r","f1"]

    t=t[t["we"]!="ftBert_both"]

    for ta in ['fixingtime','severity','priority','reopen','reassignment']:
        tt=t[t["task"]==ta]

        bert=tt["f1"][tt["we"]=="bert"]
        elmo=tt["f1"][tt["we"]=="elmo"]
        #f100=tt["f1"][(tt["we"]=="fastText") & (tt["dim"]==100)]
        #f200=tt["f1"][(tt["we"]=="fastText") & (tt["dim"]==200)]
        f300=tt["f1"][(tt["we"]=="fastText") & (tt["dim"]==300)]
        #g50=tt["f1"][(tt["we"]=="glove") & (tt["dim"]==50)]
        #g100=tt["f1"][(tt["we"]=="glove") & (tt["dim"]==100)]
        #g200=tt["f1"][(tt["we"]=="glove") & (tt["dim"]==200)]
        g300=tt["f1"][(tt["we"]=="glove") & (tt["dim"]==300)]
        word2vec=tt["f1"][(tt["we"]=="word2vec") & (tt["dim"]==300)]

        #data=np.array([bert,elmo,f100,f200,f300,g50,g100,g200,g300,word2vec])
        #print(friedmanchisquare(bert,elmo,f100,f200,f300,g50,g100,g200,g300,word2vec))
        data=np.array([bert,elmo,f300,g300,word2vec])
        print(ta+'-rq2-we-Friedman-test:',friedmanchisquare(bert,elmo,f300,g300,word2vec))
        #print(sp.posthoc_nemenyi_friedman(data.T))

        ranks = np.argsort(-data, axis=0) + 1
        mean_ranks = np.sum(ranks, axis=1) /len(bert)
        #print('mean_ranks:',mean_ranks)
        cd = Orange.evaluation.compute_CD(mean_ranks, len(bert))
        #print("cd:",cd)

        #methods=[('bert',768),('elmo',1024),('fastText',100),('fastText',200),('fastText',300),('glove',50),('glove',100),('glove',200),('glove',300),('word2vec',300)]
        methods=[('bert',768),('elmo',1024),('fastText',300),('glove',300),('word2vec',300)]

        cd_fout='rq2-we-'+ta+'.pdf'
        pp=PdfPages(cd_fout)
        cdplot=Orange.evaluation.graph_ranks(mean_ranks, methods, cd=cd, width=6, textspace=1.5)
        pp.savefig(cdplot)
        pp.close()

        #comp_list=[('bert',768),('elmo',1024),('fastText',100),('fastText',200),('fastText',300),('glove',50),('glove',100),('glove',200),('glove',300),('word2vec',300)]
        comp_list=[('bert',768),('elmo',1024),('fastText',300),('glove',300),('word2vec',300)]

        combs = np.fromiter(combinations(range(len(comp_list)),2), dtype='i,i')
        for (i,j) in combs:
            (w1,d1) = comp_list[i]
            (w2,d2) = comp_list[j]
            idat=tt["f1"][(tt["we"]==w1) & (tt["dim"]==d1)]
            jdat=tt["f1"][(tt["we"]==w2) & (tt["dim"]==d2)]
            d, res = cliffs_delta(idat, jdat)
            print(ta,comp_list[i],comp_list[j],d,res)
    #pp.close()

def compareWE2VSM(embMLRes_fin,vsmMLRes_fin):

    t=pd.read_csv(embMLRes_fin,sep=",",header=None)
    t.columns=["fd","prod","ptype","we","dim","task","ml","p","r","f1"]
    t=t[(t["we"]!="ftBert_both") & (t["ml"]=="RF")]

    vsm_t=pd.read_csv(vsmMLRes_fin,sep=",",header=None) #all vsm ml results are RF based results on vsm-tfidf features
    vsm_t.columns=["fd","prod","ptype","we","dim","task","ml","p","r","f1"]
    for ta in ['fixingtime','severity','priority','reopen','reassignment']:
        tt=t[t["task"]==ta]

        vsm=vsm_t["f1"][vsm_t["task"]==ta]
        bert=tt["f1"][tt["we"]=="bert"]
        elmo=tt["f1"][tt["we"]=="elmo"]
        #f100=tt["f1"][(tt["we"]=="fastText") & (tt["dim"]==100)]
        #f200=tt["f1"][(tt["we"]=="fastText") & (tt["dim"]==200)]
        f300=tt["f1"][(tt["we"]=="fastText") & (tt["dim"]==300)]
        #g50=tt["f1"][(tt["we"]=="glove") & (tt["dim"]==50)]
        #g100=tt["f1"][(tt["we"]=="glove") & (tt["dim"]==100)]
        #g200=tt["f1"][(tt["we"]=="glove") & (tt["dim"]==200)]
        g300=tt["f1"][(tt["we"]=="glove") & (tt["dim"]==300)]
        word2vec=tt["f1"][(tt["we"]=="word2vec") & (tt["dim"]==300)]

        #data=np.array([vsm,bert,elmo,f100,f200,f300,g50,g100,g200,g300,word2vec])
        #print(friedmanchisquare(bert,elmo,f100,f200,f300,g50,g100,g200,g300,word2vec))

        data=np.array([vsm,bert,elmo,f300,g300,word2vec])
        print('rq3-we2vsm-Friedman-test-'+ta+':',friedmanchisquare(vsm,bert,elmo,f300,g300,word2vec))
        #print(sp.posthoc_nemenyi_friedman(data.T))

        ranks = np.argsort(-data, axis=0) + 1
        mean_ranks = np.sum(ranks, axis=1) /len(bert)
        #print('mean_ranks:',mean_ranks)

        cd = Orange.evaluation.compute_CD(mean_ranks, len(bert),test='bonferroni-dunn')
        #cd = Orange.evaluation.compute_CD(mean_ranks, len(bert))
        #print("cd:",cd)

        #methods=[('vsm','tfidf'),('bert',768),('elmo',1024),('fastText',100),('fastText',200),('fastText',300),('glove',50),('glove',100),('glove',200),('glove',300),('word2vec',300)]
        methods=[('vsm','tfidf'),('bert',768),('elmo',1024),('fastText',300),('glove',300),('word2vec',300)]

        cd_fout='rq3-we2vsm-'+ta+'.pdf'
        pp=PdfPages(cd_fout)
        cdplot=Orange.evaluation.graph_ranks(mean_ranks, methods, cd=cd, cdmethod=0, width=6, textspace=1.5)
        pp.savefig(cdplot)
        pp.close()
        #comp_list=[('bert',768),('elmo',1024),('fastText',100),('fastText',200),('fastText',300),('glove',50),('glove',100),('glove',200),('glove',300),('word2vec',300)]
        comp_list=[('bert',768),('elmo',1024),('fastText',300),('glove',300),('word2vec',300)]
        for (i,j) in comp_list:
            idat=tt["f1"][(tt["we"]==i) & (tt["dim"]==j)]
            wd,wdres = wilcoxon(idat,vsm)
            print(ta,'wilcoxon:',wd,wdres)
            d, res = cliffs_delta(idat, vsm)
            print(ta,(i,j),'vsm',d,res)
    #pp.close()


def compareBertFT(embMLRes_fin):

    t=pd.read_csv(embMLRes_fin,sep=",",header=None)
    t.columns=["fd","prod","ptype","we","dim","task","ml","p","r","f1"]
    #t=t[t["ml"]=="RF"] #do not affect the conclusion too much for only RF or all MLs
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

def compareDim(embMLRes_fin,comp_list):

    t=pd.read_csv(embMLRes_fin,sep=",",header=None)
    t.columns=["fd","prod","ptype","we","dim","task","ml","p","r","f1"]

    t=t[t["we"]!="ftBert_both"]
    #t=t[(t["we"]!="ftBert_both") & (t["ml"]=="RF")]
    for ta in ['fixingtime','severity','priority','reopen','reassignment']:
        tt=t[t["task"]==ta]

        vl=[]
        for (i,j) in comp_list:
            print(i,j)
            v=tt["f1"][(tt["we"]==i) & (tt["dim"]==j)]
            vl.append(np.array(v))

        data=np.array(vl)
        print('rq2-dimsize-'+ta+'-friedman-test-'+comp_list[0][0]+':',friedmanchisquare(*data))
        print(sp.posthoc_nemenyi_friedman(data.T))

        ranks = np.argsort(-data, axis=0) + 1
        mean_ranks = np.sum(ranks, axis=1) /len(vl[0])
        print('mean_ranks:',mean_ranks)
        cd = Orange.evaluation.compute_CD(mean_ranks, len(vl[0]))
        print("cd:",cd)

        #methods=[('fastText',100),('fastText',200),('fastText',300)]
        cd_fout='rq2-dimsize-'+ta+'-'+comp_list[0][0]+'.png'
        #pp = PdfPages(cd_fout)
        cdplot=Orange.evaluation.graph_ranks(mean_ranks, comp_list, cd=cd, width=6, textspace=1.5)
        cdplot.savefig(cd_fout)
        #pp.savefig(cdplot)
        #pp.close()

        #comp_list=[('fastText',100),('fastText',200),('fastText',300)]
        combs = np.fromiter(combinations(range(len(comp_list)),2), dtype='i,i')
        for (i,j) in combs:
            (w1,d1) = comp_list[i]
            (w2,d2) = comp_list[j]
            idat=tt["f1"][(tt["we"]==w1) & (tt["dim"]==d1)]
            jdat=tt["f1"][(tt["we"]==w2) & (tt["dim"]==d2)]
            d, res = cliffs_delta(idat, jdat)
            print(ta,comp_list[i],comp_list[j],d,res)
    #pp.close()
if __name__ == '__main__':
    embMLFin = sys.argv[1] #ML res
    vsmMLFin = sys.argv[2]
    #cdFout = sys.argv[3]

    #pp = PdfPages(cdFout)

    comp_list=[('fastText',100),('fastText',200),('fastText',300)]
    compareDim(embMLFin,comp_list)
    comp_list=[('glove',50),('glove',100),('glove',200),('glove',300)]
    compareDim(embMLFin,comp_list)

    compareML(embMLFin)
    compareWE(embMLFin)
    compareWE2VSM(embMLFin,vsmMLFin)
    compareBertFT(embMLFin)
    #pp.close()
