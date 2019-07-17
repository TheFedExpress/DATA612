# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 19:25:55 2019

@author: pgood
"""
import pandas as pd
from nltk.stem import WordNetLemmatizer, SnowballStemmer
import re
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from gensim import corpora, models
import numpy as np

book_extracts = pd.read_csv('book_extracts.csv')

def lemmatize_stemming(text):
    stemmer = SnowballStemmer('english')
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

def preprocess(desc):
    words = []
    try:
        for item in simple_preprocess(desc, min_len = 3):
            words.append(lemmatize_stemming(item))
        return words
    except(TypeError):
        return np.nan



book_extracts['words'] = book_extracts['desc'].map(preprocess)
book_words = book_extracts[['book_id', 'words']].dropna()

dictionary = corpora.Dictionary(book_words['words'])
dictionary.filter_extremes(no_below=3, no_above=0.5, keep_n=20000)
dictionary.compactify()
corpus = [dictionary.doc2bow(item) for item in book_words['words']]

corpus_out = []
for i in range(len(corpus)):
    recreate = [dictionary.get(tup[0]) for tup in corpus[i] for j in range(tup[1])]
    text = ' '.join(recreate)
    corpus_out.append(text)
        
tidy_words = pd.DataFrame(corpus_out, columns = ['text'])
tidy_words.to_csv('tidy_words.csv', index = False)
book_words.to_csv('book_to_id.csv')