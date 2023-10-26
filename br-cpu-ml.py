import sys
import time
import pandas
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from imblearn.over_sampling import RandomOverSampler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import precision_recall_fscore_support

def run_classification(embFea_fin, label_fin, ml_name):
    X = np.array(pandas.read_csv(embFea_fin,sep = " ", header=None))
    Y = np.array(pandas.read_csv(label_fin, sep = " ", header=None))
    kf = StratifiedKFold(n_splits=10)
    p=[]
    r=[]
    f=[]
    ros = RandomOverSampler()
    for i, (tr,te) in enumerate(kf.split(X,Y)):
        x, y = ros.fit_resample(X[tr], Y[tr])
        if ml_name == "Logistic":
            clf = LogisticRegression(max_iter=5000)
        if ml_name == "SVM":
            clf = SVC(decision_function_shape='ovr')
        if ml_name == "NB":
            clf = GaussianNB()
        if ml_name == "RF":
            clf = RandomForestClassifier()
        clf.fit(x,y)
        y_pred=clf.predict(X[te])

        precision, recall, f1,_ = precision_recall_fscore_support(Y[te].get(), y_pred.get(), average='weighted')
        p.append(precision)
        r.append(recall)
        f.append(f1)
    print(str(sum(p)/len(p))+","+str(sum(r)/len(r))+","+str(sum(f)/len(f)))

if __name__ == '__main__':
    embFea_fin = sys.argv[1] #only features
    label_fin = sys.argv[2] #only corresponding labels
    ml_name = sys.argv[3] #which ML to apply
    run_classification(embFea_fin, label_fin, ml_name)
