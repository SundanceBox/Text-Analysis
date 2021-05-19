# NOTE: This chunk of code is only for use with Research Desktop. You will get an error if you try to run this code on your personal device!!

import sys
import os
sys.path.insert(0,"/N/u/cyberdh/Carbonate/dhPyEnviron/lib/python3.6/site-packages")
os.environ["NLTK_DATA"] = "/N/u/cyberdh/Carbonate/dhPyEnviron/nltk_data"


# Include necessary packages for notebook 

from textblob import TextBlob
from nltk.corpus import stopwords
import re
import string
import pandas as pd
import gensim
from gensim.models.phrases import Phrases, Phraser
from gensim.utils import simple_preprocess
import spacy
import wordcloud
import glob
import matplotlib.pyplot as plt

# File paths
homePath = os.environ["HOME"]
dataHome = os.path.join(homePath, "Text-Analysis-master", "data")
corpusRoot = os.path.join(dataHome, "shakespeareFolger")
directRoot = os.path.join(dataHome, "starTrek")
dataResults = os.path.join(homePath, "Text-Analysis-master", "Output")


# Set needed variables
corpusLevel = "lines"
singleFile = "Hamlet.txt"
nltkStop = True
customStop = True
spacyLem = True
ng = 2
stopLang = 'english'
lemLang = "en"
encoding = "UTF-8"
errors = "ignore"
stopWords = []
ngramList = []


# Stopwords

# NLTK Stop words
if nltkStop is True:
    stopWords.extend(stopwords.words(stopLang))

    stopWords.extend(['would', 'said', 'says', 'also', 'good', 'lord', 'come', 'let'])


# Add own stopword list

if customStop is True:
    stopWordsFilepath = os.path.join(homePath, "Text-Analysis-master", "data", "earlyModernStopword.txt")

    with open(stopWordsFilepath, "r",encoding = encoding) as stopfile:
        stopWordsCustom = [x.strip() for x in stopfile.readlines()]

    stopWords.extend(stopWordsCustom)


# Functions

# Text Cleaning

def sentToWords(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations

def removeStopwords(texts):
    return [[word for word in simple_preprocess(str(doc)) if word not in stopWords] for doc in texts]

def makeLemma(tokens):
    dataWords = tokens
    if spacyLem is True:
        def lemmatization(tokens):
            """https://spacy.io/api/annotation"""
            textsOut = []
            for sent in tokens:
                doc = nlp(" ".join(sent)) 
                textsOut.append([token.lemma_ for token in doc if token.lemma_ != '-PRON-'])
            return textsOut
        
        # Initialize spacy language model, eliminating the parser and ner components
        nlp = spacy.load(lemLang, disable=['parser', 'ner'])
    
        # Do lemmatization
       
        dataLemmatized = lemmatization(dataWords)
       
        return dataLemmatized
    
    else:
        
        return dataWords
# Reading in the Text

if corpusLevel == "lines":
    textFilepath = os.path.join(corpusRoot, singleFile)
    docs=[]
    with open(textFilepath, "r", encoding = encoding, errors = errors) as f:
        for line in f:
            stripLine = line.strip()
            if len(stripLine) == 0:
                continue
            docs.append(stripLine.split())
    
    words = list(sentToWords(docs))
    stop = removeStopwords(words)
    lemma = makeLemma(stop)
    tokens = [item for sublist in lemma for item in sublist]
elif corpusLevel == "files":
    docs = []
    
    for root, subdirs, files in os.walk(corpusRoot):
        
        for filename in files:
            
            # skip hidden file
            if filename.startswith('.'):
                continue
            
            textFilepath = os.path.join(root, filename)
            
            with open(textFilepath, "r", encoding = encoding, errors = errors) as f:
                docs.append(f.read().strip('\n').splitlines())
        
        words = list(sentToWords(docs))
        stop = removeStopwords(words)
        lemma = makeLemma(stop)
        tokens = [item for sublist in lemma for item in sublist]
elif corpusLevel == "direct":
    paths = []
    docs = []
   
    dataPath = os.path.join(directRoot)
    for folder in sorted(os.listdir(dataPath)):
        if not os.path.isdir(os.path.join(dataPath, folder)):
            continue
        for file in sorted(os.listdir(os.path.join(dataPath, folder))):
            paths.append(((dataPath, folder, file)))
    df = pd.DataFrame(paths, columns = ["Root", "Folder", "File"])
    df["Paths"] = df["Root"].astype(str) +"/" + df["Folder"].astype(str) + "/" + df["File"].astype(str)
    for path in df["Paths"]:
        if not path.endswith(".txt"):
            continue
        with open(path, "r", encoding = encoding, errors = errors) as f:
            docs.extend(f.read().strip().split())
    
    words = list(sentToWords(docs))
    stop = removeStopwords(words)
    lemma = makeLemma(stop)
    tokens = [item for sublist in lemma for item in sublist]


# Convert text to a str object so we can find ngrams later.

cleanTokens = ' '.join(tokens)


# Find Ngrams

blob = TextBlob(cleanTokens)

nGrams = blob.ngrams(n=ng)


# Convert ngrams to a list

for wlist in nGrams:
   ngramList.append(' '.join(wlist))


# Now we make our dataframe. 
df = pd.DataFrame(ngramList)
df = df.replace(' ', '_', regex=True)
dfCounts = df[0].value_counts()
countsDF = pd.DataFrame(dfCounts)
countsDF.reset_index(inplace = True)
df_C = countsDF.rename(columns={'index':'ngrams',0:'freq'})
df_C.set_index(df_C['ngrams'], inplace = True)
df_C['ngrams'] = df_C['ngrams'].astype(str)
dfNG = df_C.sort_values('freq', ascending = False)


# Now lets see what our dataframe looks like. 
dfNG.head(10)


# Plot our wordcloud

# Variables
maxWrdCnt = 500
bgColor = "black"
color = "Dark2"
minFont = 10
width = 800
height = 400
figureSz = (20,10)
wcOutputFile = "ngramWordCloud.png"
imgFmt = "png"
dpi = 600

# Ngram Stopwords
stopwords = ["ngrams","love_love","ha_ha", "fie_fie", "know_know", "hamlet_hamlet", "god_god", "life_life"]
text = dfNG[~dfNG['ngrams'].isin(stopwords)]

# Wordcloud aesthetics

wc = wordcloud.WordCloud(background_color = bgColor, width = width, height = height, max_words = maxWrdCnt, colormap = color, min_font_size = minFont).generate_from_frequencies(text['freq'])

# show
plt.figure(figsize = figureSz)
plt.imshow(wc, interpolation = 'bilinear')
plt.axis("off")
plt.tight_layout()
    
# save graph as an image to file
plt.savefig(os.path.join(dataResults, wcOutputFile), format = imgFmt, dpi = dpi, bbox_inches = 'tight')
    
plt.show()
