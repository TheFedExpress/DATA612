# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 14:28:04 2019

@author: pgood
"""

import pandas as pd
movies = pd.read_csv(r'C:\Users\pgood\OneDrive\Documents\DATA612\the-movies-dataset\ratings.csv')

top_movies = movies.groupby('movieId').size().sort_values(ascending = False).head(2000)
top_users = movies.groupby('userId').size().sort_values(ascending = False).head(10000)

movies_medium = (movies.set_index('movieId')
    .loc[top_movies]
    .reset_index()
    .set_index('userId')
    .loc[top_users]
    .reset_index()
    .dropna()
)
movies_medium.to_csv('movies_medium.csv')