import os
import sys
import time
import pandas as pd
import traceback
import sklearn
from imblearn.over_sampling import RandomOverSampler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import precision_recall_fscore_support
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import RandomOverSampler

def run_classification(embFea_fin, label_fin, sampleRatio, featureRatio):
    try:
        X = pd.read_csv(embFea_fin,sep = "\s+|\t+|\s+\t+|\t+\s+", header=None, engine="python",encoding='UTF-8').values
        Y = pd.read_csv(label_fin, sep = "\s+|\t+|\s+\t+|\t+\s+", header=None, engine="python",encoding='UTF-8').values.flatten()

        sampleRatio=float(sampleRatio)
        if featureRatio not in ["sqrt", "log2", "auto"]:#options besides these are all float values
            featureRatio=float(featureRatio)
        try:
            kf = StratifiedKFold(n_splits=10)
            ros = RandomOverSampler()
            p=[]
            r=[]
            f=[]
            for tr,te in kf.split(X,Y):
                x, y = ros.fit_resample(X[tr], Y[tr])
                clf = RandomForestClassifier(max_features=featureRatio,max_samples=sampleRatio,n_jobs=20,max_depth=16) #cuml only support max_depth=16
                clf.fit(x,y)
                y_pred=clf.predict(X[te])
                precision, recall, f1,_ = precision_recall_fscore_support(Y[te], y_pred, average='weighted')
                p.append(precision)
                r.append(recall)
                f.append(f1)
            print(str(sum(p)/len(p))+","+str(sum(r)/len(r))+","+str(sum(f)/len(f)))
        except:
            traceback.print_exc()
    except:
        traceback.print_exc()

if __name__ == '__main__':
    embFea_fin = sys.argv[1] #only features
    label_fin = sys.argv[2] #only corresponding labels
    splRatio = sys.argv[3]
    feaRatio = sys.argv[4]
    run_classification(open(embFea_fin), open(label_fin), splRatio, feaRatio)
