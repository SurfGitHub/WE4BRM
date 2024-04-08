import sys
import os
import time
import cupy
import cudf
import itertools
import traceback
from cupyx.scipy.sparse import csr_matrix
from cuml.feature_extraction.text import TfidfVectorizer
from cuml.naive_bayes import GaussianNB
from cuml.ensemble import RandomForestClassifier
from cuml.svm import SVC
from cuml.linear_model import LogisticRegression
from imblearn.over_sampling import RandomOverSampler
from cuml.model_selection import StratifiedKFold
from sklearn.metrics import precision_recall_fscore_support

def run_classification(br_fin, ml_name, dat_info, para_fout):
    corpus=[]
    label=[]
    try:
        for br in br_fin.readlines():
            lab, bid, text = br.strip("\n").strip().split(" ",2)
            corpus.append(text)
            label.append(int(lab))

        dat = cudf.DataFrame({'lab':label,'text':corpus})
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(dat["text"]) #csr_matrix, sparse
        Y = dat["lab"].to_cupy()

        ###for paratune:
        spl=[1.0,0.8,0.6,0.4,0.2]
        fea=["sqrt","log2","0.1","0.2","0.3","0.4","0.5"]
        for (sampleRatio,featureRatio) in itertools.product(spl, fea):
            if featureRatio in ["0.1", "0.2", "0.3","0.4","0.5"]:
                featureRatio=float(featureRatio)

            try:
                kf = StratifiedKFold(n_splits=10)
                ros = RandomOverSampler()
                p=[]
                r=[]
                f=[]
                for tr,te in kf.split(X.todense(),Y):
                    x, y = ros.fit_resample(X[tr].get(), Y[tr].get()) #use get() to convert cuml to scipy data type, then do balance
                    x = csr_matrix(x)
                    y = cupy.asarray(y)
                    if ml_name == "RF":
                        clf = RandomForestClassifier(max_features=featureRatio,max_samples=sampleRatio,n_streams=10) #clf = RandomForestClassifier()
                    #in cuml, RF does not support csr_matrix but dense matrix
                        clf.fit(x.todense(),y)
                        y_pred=clf.predict(X[te].todense())

                    precision, recall, f1,_ = precision_recall_fscore_support(Y[te].get(), y_pred.get(), average='weighted')
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
    ml_name = sys.argv[2] #which ML to apply
    dat_info = sys.argv[3] #dat_info is used to describe the information of the dataset for BRM task classification model building
    para_fout = sys.argv[4]
    run_classification(open(br_fin,'r'), ml_name, dat_info, open(para_fout, mode = 'a'))
