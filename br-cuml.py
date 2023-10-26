import sys
import time
import cupy
import cudf
from cuml.naive_bayes import GaussianNB
from cuml.ensemble import RandomForestClassifier
from cuml.svm import SVC
from cuml.linear_model import LogisticRegression
from imblearn.over_sampling import RandomOverSampler
from cuml.model_selection import StratifiedKFold
from sklearn.metrics import precision_recall_fscore_support

def run_classification(embFea_fin, label_fin, ml_name):
    X = (cudf.read_csv(embFea_fin,sep = " ", header=None)).to_cupy()
    Y = (cudf.read_csv(label_fin, sep = " ", header=None)).to_cupy()
    kf = StratifiedKFold(n_splits=10)
    p=[]
    r=[]
    f=[]
    ros = RandomOverSampler()
    for tr,te in kf.split(X,Y):
        x, y = ros.fit_resample(X[tr].get(), Y[tr].get()) #use get() to get a numpy array, and then blanace the training data set
        if ml_name == "Logistic":
            clf = LogisticRegression(max_iter=5000)
        if ml_name == "SVM":
            clf = SVC(multiclass_strategy='ovr')
        if ml_name == "NB":
            clf = GaussianNB()
        if ml_name == "RF":
            clf = RandomForestClassifier()
        x = cupy.asarray(x)
        y = cupy.asarray(y)
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
