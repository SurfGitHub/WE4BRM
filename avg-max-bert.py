import sys
import os
os.environ['CURL_CA_BUNDLE'] = ''

from flair.embeddings import TransformerWordEmbeddings, DocumentPoolEmbeddings
from flair.embeddings import TransformerDocumentEmbeddings
from flair.data import Sentence

def get_bert_avg_max_pooling(br_fin, avgp_fout, maxp_fout):
    #sentence1 = Sentence('The grass is green')
    #wordBert.embed(sentence1)
    #print("word by one one")
    #for token in sentence1:
    #    print(token)
    #    print(token.embedding)

    ##docBert is different with pooling doc bert based on word embeddings
    #docBert = TransformerDocumentEmbeddings('bert-base-uncased', layers="-1", layer_mean=False)
    #sentence2 = Sentence('The grass is green')
    #docBert.embed(sentence2)
    #print("direct whole doc")
    #print(sentence2.embedding)

    #wordBert = TransformerWordEmbeddings('bert-base-uncased', layers="-1", layer_mean=False)
    #avgPooling = DocumentPoolEmbeddings([wordBert],pooling='mean')
    #maxPooling = DocumentPoolEmbeddings([wordBert],pooling='max')
    #sentence3 = Sentence('The grass is green')
    #sentence4 = Sentence('The grass is green')

    #avgPooling.embed(sentence3)
    #print("avgPooling words")
    #print(sentence3.embedding)

    #maxPooling.embed(sentence4)
    #print("maxPooling words")
    #print(sentence4.embedding)

    wordBert = TransformerWordEmbeddings('bert-base-uncased', layers="-1", layer_mean=False)
    avgPooling = DocumentPoolEmbeddings([wordBert],pooling='mean')
    maxPooling = DocumentPoolEmbeddings([wordBert],pooling='max')
    avgL=[]
    maxL=[]
    for br in br_fin.readlines():
        if(len(br.strip("\n").strip().split(" "))<=1):continue
        bid, text=br.strip("\n").strip().split(" ",1)
        #print(bid+", "+text)
        avgs=Sentence(text)
        maxs=Sentence(text)

        avgPooling.embed(avgs)
        maxPooling.embed(maxs)

        avgv = ['{:.7f}'.format(i) for i in avgs.embedding.tolist()]
        maxv = ['{:.7f}'.format(i) for i in maxs.embedding.tolist()]
        avgv=str(bid) + "," + " ".join(list(map(str, avgv)))
        maxv=str(bid) + "," + " ".join(list(map(str, maxv)))
        avgL.append(avgv)
        maxL.append(maxv)

    avgp_fout.write("\n".join(avgL)+"\n")
    maxp_fout.write("\n".join(maxL)+"\n")

if __name__ == '__main__':
    brFin = sys.argv[1] #format:bid, token1 token2 ... tokenN
    avgpFout = sys.argv[2] #the average pooling output file
    maxpFout = sys.argv[3] #the max pooling output file
    get_bert_avg_max_pooling(open(brFin,'r'), open(avgpFout,'w'), open(maxpFout,'w'))
