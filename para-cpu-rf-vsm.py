import sklearn
import sys
import time
import pandas as pd
import itertools
import traceback
import os
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from imblearn.over_sampling import RandomOverSampler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import precision_recall_fscore_support
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import RandomOverSampler

def run_classification(br_fin, dat_info, para_fout):
    corpus=[]
    label=[]
    try:
        for br in br_fin.readlines():
            if(len(br.strip("\n").strip().split(" "))<3):continue
            lab, bid, text = br.strip("\n").strip().split(" ",2)
            corpus.append(text)
            label.append(int(lab))

        dat = pd.DataFrame({'lab':label,'text':corpus})
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(dat["text"]) #csr_matrix, sparse
        Y = dat["lab"]

        ###for paratune:
        spl=[1.0,0.8,0.6,0.4,0.2]
        fea=["sqrt","log2","0.1","0.2","0.3","0.4","0.5"]
        for (sampleRatio,featureRatio) in itertools.product(spl, fea):
            if featureRatio in ["0.1", "0.2", "0.3","0.4","0.5"]:
                featureRatio=float(featureRatio)
            try:
                kf = StratifiedKFold(n_splits=10)
                p=[]
                r=[]
                f=[]
                ros = RandomOverSampler()
                for tr,te in kf.split(X.todense(),Y):
                    x, y = ros.fit_resample(X[tr], Y[tr])
                    x = csr_matrix(x)
#                    clf = RandomForestClassifier(max_features=featureRatio,max_samples=sampleRatio,n_jobs=20,max_depth=16)
                    clf = RandomForestClassifier(max_features=featureRatio,max_samples=sampleRatio,n_jobs=20)
                    clf.fit(x,y)
                    y_pred=clf.predict(X[te])
                    precision, recall, f1,_ = precision_recall_fscore_support(Y[te], y_pred, average='weighted')
                    p.append(precision)
                    r.append(recall)
                    f.append(f1)
                perf=dat_info+","+str(sampleRatio)+","+str(featureRatio)+","+str(sum(p)/len(p))+","+str(sum(r)/len(r))+","+str(sum(f)/len(f))
                para_fout.write(perf+"\n")
                para_fout.flush()
                os.fsync(para_fout)
            except:
                print(dat_info+","+str(sampleRatio)+","+str(featureRatio))
                traceback.print_exc()
                continue
            #break
    except:
        traceback.print_exc()

if __name__ == '__main__':
    br_fin = sys.argv[1] #format:label bid token1 token2 ... tokenN
    dat_info = sys.argv[2] #dat_info is used to describe the information of the dataset for BRM task classification model building
    para_fout = sys.argv[3]
    run_classification(open(br_fin,'r'), dat_info, open(para_fout, mode = 'a'))
