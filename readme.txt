Step1: download the bug reports from the bug tracking systems of Eclipse and Mozilla foundations
The bug reports of Eclipse foundation could be downloaded from https://bugs.eclipse.org/
The bug reports of Eclipse foundation could be downloaded from https://bugzilla.mozilla.org
You can try to write your own crawler to crawl these bug data, or try to use our script in the folder scrapy whose README.md file describes how to use it.
We did not provide the raw data of all bug reports as they are large files.

Step2: Currently we downloaded the bug reports of Eclipse or Mozilla in one single XML file. As we choose the top 10 products with most bug reports from each foundation for experiments, we need to first count the number of each product and find the top10 products.
The two files, i.e., eclipse.brCnt and mozilla.brCnt contains the total number of bug reports for each product of Eclipse and Mozilla.
We would choose the top 10 products with most bug reports as experimental products. The following two scripts are used to retrieve needed information for experiments.

(S2.1) use the get_brBasicInfo.py to get the file eclipse/mozilla_brBasic (includes productName,bugId,status,resolution,priority,severity,duplicateId,fixingTime,createTime,deltaTime from each bug report).
python get_brBasicInfo.py eclipse.xml eclipse_brBasic eclipse.abNorbr eclipse  #please replace eclipse with mozilla for the Mozilla foundation.

(S2.2) use the bugs2label.sh to label each bug report for five BRM classification tasks. This shell script will call get_top10prod_closedbugs.py to get the *top10* folder that contains bugIDs of the top 10 products with most bug reports. And then create the *label* folder that contains the labeled bug reports for five BRM classificationt tasks.
./bugs2label.sh  

Step3: retrieve the textual title and description items from bug reports and preprocess it.
This step could get a *afterPreprocess* folder that contains the preprocessed title/description, which are the input for the WE and VSM models.
python3 get_titleDesc.py mozilla.xml top10/mozilla.top10.id mo mabo mozilla

Step4: After we obtain the labels as well as the preprocessed title/description, we can start to use the five pre-trained WE to represent the semantics of each bug report; also, fine tune the general pre-trained BERT and use it to represent bug reports.  
(S4.1) use five general pre-trained WE models to represent each bug report.
Before using these WE models, you should download them from their official websites first.
Note that, besides average pooling strategy, we also support max pooling for possible further exploration.
./run_glove.sh eclipse #can replace eclipse with mozilla
./run_fasttext.sh eclipse #can replace eclipse with mozilla
./run_word2vec.sh eclipse #can replace eclipse with mozilla
./run_bert.sh eclipse #can replace eclipse with mozilla
./run_elmo.sh eclipse #can replace eclipse with mozilla

(S4.2) use the xxx to get the finetuned BERT and use it to obtain the finetuned WE vectors for each bug report

Step5: run WE-based BRM tasks (WEs include general pre-trained WEs and fine-tuned BERT)
(S5.1) WE-based BRM classification tasks
./run_ml.sh eclipse 0 avg #please replace eclipse with mozilla. avg means average pooling. max means maxpooling
./pcf_run_ml.sh eclipse 0 avg #please replace eclipse with mozilla. This script is used to run the three large products namely platform, core, and firefox, we only use their latest 5w bug reports for classification model construct.

(S5.2) WE-based duplicate bug report detection task 
./run_dup.sh eclipse avg

Step6: run VSM-based BRM tasks
(S6.1) VSM-based BRM classification tasks
./run_cpu_vsm.sh eclipse #CPU version
./run_vsm.sh eclipse 0 #GPU version, 0 is the index of the GPU used, change it based on your case

(S6.2) VSM-based duplicate bug report detection task 
./run_vsmDup.sh eclipse 0

Step7: perform hyper parameter tuning of RF for BRM classification tasks
(S7.1) WE-based RF with hyperparameter tuning
./para_run_emb.sh mozilla 0 #can replace mozilla with eclipse. 
In default, we use the GPU version, if GPU out of memory, please use the cpu version: para-cpu-emb-classification.py
./para_run_cpu_4missing_emb.sh mozilla #can replace mozilla with eclipse

(S7.2) VSM-based RF with hyperparameter tuning
./para_run_cpu_vsm.sh mozilla #can replace mozilla with eclipse. CPU version.

In default, we use the CPU version for vsm-based RF parameter tuning as in many cases, one single GPU will encounter out of memory error. But we also provide the GPU version:
./para_run_vsm.sh eclipse 0 #can replace eclipse with mozilla.

###########statistical tests to RQs#################
(RQ1-RQ4 in Sect.4):
python wiltest.py EM_avg.ml EM_vsm.ml > rqs-avg-emb-ml.testRes
python dup-wiltest.py EM-embDup.recallN EM-vsmDup.recallN 'avg' > rqs-dup.testRes

(hyperparameter tuning in Sect.5.1):
python paraAnalysis.py emb.sorted vsm.sorted > para.testRes
