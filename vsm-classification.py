import sys
import time
import cupy
import cudf
from cupyx.scipy.sparse import csr_matrix
from cuml.feature_extraction.text import TfidfVectorizer
from cuml.naive_bayes import GaussianNB
from cuml.ensemble import RandomForestClassifier
from cuml.svm import SVC
from cuml.linear_model import LogisticRegression
from imblearn.over_sampling import RandomOverSampler
from cuml.model_selection import StratifiedKFold
from sklearn.metrics import precision_recall_fscore_support

def run_classification(br_fin, ml_name):
    corpus=[]
    label=[]
    for br in br_fin.readlines():
        lab, bid, text = br.strip("\n").strip().split(" ",2)
        corpus.append(text)
        label.append(int(lab))

    dat = cudf.DataFrame({'lab':label,'text':corpus})
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(dat["text"]) #csr_matrix, sparse
    Y = dat["lab"].to_cupy()

    kf = StratifiedKFold(n_splits=10)
    p=[]
    r=[]
    f=[]
    ros = RandomOverSampler()
    for tr,te in kf.split(X.todense(),Y):
        x, y = ros.fit_resample(X[tr].get(), Y[tr].get()) #use get() to convert cuml to scipy data type, then do balance
        x = csr_matrix(x)
        y = cupy.asarray(y)
        if ml_name == "Logistic":
            clf = LogisticRegression(max_iter=5000)
        elif ml_name == "SVM":
            clf = SVC(multiclass_strategy='ovr')
        elif ml_name == "NB":
            clf = GaussianNB()
        elif ml_name == "RF":
            clf = RandomForestClassifier()

        if ml_name in "Logistic" "NB":#in cuml, Logistic and NB support csr_matrix
            clf.fit(x,y)
            y_pred=clf.predict(X[te])
        elif ml_name in "SVM" "RF": #in cuml, SVM and RF does not support csr_matrix but dense matrix
            clf.fit(x.todense(),y)
            y_pred=clf.predict(X[te].todense())

        precision, recall, f1,_ = precision_recall_fscore_support(Y[te].get(), y_pred.get(), average='weighted')
        p.append(precision)
        r.append(recall)
        f.append(f1)
    print(str(sum(p)/len(p))+","+str(sum(r)/len(r))+","+str(sum(f)/len(f)))

if __name__ == '__main__':
    br_fin = sys.argv[1] #format:label bid token1 token2 ... tokenN
    ml_name = sys.argv[2] #which ML to apply
    run_classification(open(br_fin,'r'), ml_name)
