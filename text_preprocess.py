#import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re

#split camelCase, and keep the original word
def split_camel_case(s):
    splitted = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', s)).split()
    if splitted and splitted != [s]:
        return [s] + splitted
    return [s] if not splitted else splitted

def preprocess(text):
    #remove non-alpha characters, and replace them with blank space
    text = re.sub(r'[^a-zA-Z]',' ',text)
    #Tokenization
    tokens = word_tokenize(text)
    all_tokens = []
    #split camelCaseWords, and transfer words into lower case
    for token in tokens:
        tc = split_camel_case(token)
        ts = [t.lower() for t in tc]
        all_tokens.extend(ts)

    #remove stopwords, perform Porter stemming and further remove single-charater words
    stop_words = set(stopwords.words('english'))
    porter_stemmer = PorterStemmer()
    res=[]
    for t in all_tokens:
        if t not in stop_words: #only consider those non-stop-words
            t_stem = porter_stemmer.stem(t)
            if(len(t_stem)>1): #remove single-charater words
                res.append(t_stem)
    return " ".join(res)
