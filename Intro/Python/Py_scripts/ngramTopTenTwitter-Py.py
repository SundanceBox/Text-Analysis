# NOTE: This chunk of code is only for use with Research Desktop. You will get an error if you try to run this code on your personal device!!

import sys
import os
sys.path.insert(0,"/N/u/cyberdh/Carbonate/dhPyEnviron/lib/python3.6/site-packages")
os.environ["NLTK_DATA"] = "/N/u/cyberdh/Carbonate/dhPyEnviron/nltk_data"


# Include necessary packages for notebook 

from textblob import TextBlob
from nltk.corpus import stopwords
import nltk
import re
import string
import pandas as pd
from collections import Counter, defaultdict
import numpy as np
import operator
import glob
import csv
import json
import zipfile
import math

import matplotlib.pyplot as plt

get_ipython().magic('matplotlib inline')


# Set needed variables

source = "*"
fileType = ".csv"
nltkStop = True
customStop = False
ng = 2
stopLang = "english"
stopWords = []
cleanText = []
ngramList = []

#print(" ".join(stopwords.fileids()))


# File paths

homePath = os.environ['HOME']
dataHome = os.path.join(homePath, "Text-Analysis-master", "data")
dataResults = os.path.join(homePath, "Text-Analysis-master", "Output")
if fileType == ".csv":
    dataRoot = os.path.join(dataHome, "twitter", "CSV", "parkland")
else:
    dataRoot = os.path.join(dataHome, "twitter", "JSON")


# Stopwords

# NLTK Stop words
if nltkStop is True:
    stopWords.extend(stopwords.words(stopLang))
    
    stopWords.extend(['amp','rt', 'xo_karmin_ox', 'neveragain', 'ð', 'â', 'ï', 'emma4change', 'could', 'us'])


# Add own stopword list

if customStop is True:
    stopWordsFilepath = os.path.join(dataHome, "earlyModernStopword.txt")

    with open(stopWordsFilepath, "r",encoding = 'utf-8') as stopfile:
        stopWordsCustom = [x.strip() for x in stopfile.readlines()]

    stopWords.extend(stopWordsCustom)


# Functions

def textClean(text):
    
    text = text.strip().lower()
    
    tweets = re.sub(r"http\S+", "", text)
    
    tokens = re.split(r'\W+', tweets )
    
    # remove empty string
    tokens = [t for t in tokens if t]
    
    # remove digits
    tokens = [t for t in tokens if not t.isdigit()]
    
    # built-in stop words list
    tokens = [t for t in tokens if t not in stopWords]
        
    # remove punctuation
    puncts = list(string.punctuation)
    puncts.append('--')

    tokens = [t for t in tokens if t not in puncts]

    return tokens


# Unzip files

direct = dataRoot
allZipFiles = glob.glob(os.path.join(dataRoot, "*.zip"))
for item in allZipFiles:
    fileName = os.path.splitext(direct)[0]
    zipRef = zipfile.ZipFile(item, "r")
    zipRef.extractall(fileName)
    zipRef.close()
    os.remove(item)


# Reading in .csv files

if fileType == ".csv":
    all_files = glob.glob(os.path.join(dataRoot, source + fileType))     
    df_all = (pd.read_csv(f, encoding ='ISO-8859-1') for f in all_files)
    cc_df = pd.concat(df_all, ignore_index=True)
    cc_df = pd.DataFrame(cc_df, dtype = 'str')
    tweets = cc_df['text'].values.tolist()
    content = '\n'.join(tweets)
    cleanTokens = textClean(content)

    print('Finished tokenizing text {}\n'.format(all_files))


# Reading in JSON files

if fileType == ".json":
    for filename in glob.glob(os.path.join(dataRoot, source + fileType)):
        with open(filename, 'r', encoding = "utf-8") as jsonData:
            tweets = []
            for line in jsonData:
                tweets.append(json.loads(line))
    df = pd.DataFrame(tweets)
    data = df['text'].tolist()
    content = '\n'.join(data)
    cleanTokens = textClean(content)

    print('Finished tokenizing text {}\n'.format(filename))


# Convert text to a str object so we can find ngrams later.

cleanText = ' '.join(cleanTokens)


# Find Ngrams

blob = TextBlob(cleanText)

if ng == 1: 
    nGrams = blob.ngrams(n=1)
if ng == 2:
    nGrams = blob.ngrams(n=2)
if ng == 3:
    nGrams = blob.ngrams(n=3)


# Convert ngrams to a list

for wlist in nGrams:
   ngramList.append(' '.join(wlist))


# Make dataframe. 
df = pd.DataFrame(ngramList)
dfCounts = df[0].value_counts()
countsDF = pd.DataFrame(dfCounts)
countsDF.reset_index(inplace = True)
df_C = countsDF.rename(columns={'index':'ngrams',0:'freq'})
df_C['ngrams'] = df_C['ngrams'].astype(str)
dfNG = df_C.sort_values('freq', ascending = False)


# Now lets see what our dataframe looks like.
dfNG.head(10)


# Plot our bargraph

# Variables
n = 10
outputFile = "ngramTopTenTwitter.svg"
fmt = 'svg'
dpi = 300
angle = 70
title = 'Top 10 Ngrams, Shakespeare'
color = ['red','orange', 'yellow', 'green', 'blue','darkorchid', 'darkred', 'darkorange','gold', 'darkgreen']
labCol = 'red'
ngramStop = ["parkland shooter","parkland students", "kidding forgetting", "forgetting come"]

# Ngram Stopwords
text = dfNG[~dfNG['ngrams'].isin(ngramStop)]
dfTN = text[0:n]

# Plot
plt.rcdefaults()

plt.bar(dfTN['ngrams'], dfTN['freq'], align = 'center', alpha = 0.5, color = color)
    

        
plt.xticks(dfTN['ngrams'])
plt.xticks(rotation = angle)
        
xlabel = plt.xlabel('Ngrams')
xlabel.set_color(labCol)
ylabel = plt.ylabel('Frequency')
ylabel.set_color(labCol)
    
high = max(dfTN['freq'])
low = 0
    
plt.ylim(low, math.ceil(high + 0.1 * (high - low)))
    
for xpos, count in zip(dfTN['ngrams'], dfTN['freq']):
    
    plt.text(x = xpos, y = count + 1, s = str(count), ha = 'center', va = 'bottom')

plt.title(title)
 
plt.savefig(os.path.join(dataResults, outputFile), format = fmt, dpi = dpi, bbox_inches = 'tight')
    
plt.show()
