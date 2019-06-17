# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 23:30:58 2019

@author: pgood
"""

import pandas as pd
import gensim
from surprise import Reader
from surprise import Dataset
from surprise.prediction_algorithms.knns import KNNWithZScore, KNNBaseline, KNNBasic
from surprise.model_selection import GridSearchCV

movies = pd.read_csv(r'movies_medium.csv').drop(['Unnamed: 0', 'timestamp'], axis = 1).dropna()
metadata = pd.read_csv(r'C:\Users\pgood\OneDrive\Documents\DATA612\the-movies-dataset\movies_metadata.csv')


reader = Reader(rating_scale=(1, 5))

data = Dataset.load_from_df(movies, reader)

param_grid = {'k' : [30,40,50], 
              'sim_options' : {'user_based': [False, True], 
              'name': ['cosine', 'pearson', 'pearson_baseline', 'MSD']},
              
 }
cv = GridSearchCV(KNNWithZScore, param_grid, cv = 5, n_jobs = -1)
cv.fit(data)
print(cv.best_score['rmse'])