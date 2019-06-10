# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 13:32:47 2019

@author: pgood
"""

import pandas as pd
from sklearn.model_selection import train_test_split

music = (pd.read_csv('ratings_digital_music.csv', header = None, names = ['user', 'item', 'rating', 'timestamp'])
    .drop('timestamp', axis = 1)
  )

user_counts = music.groupby('user').count()['item']
item_counts = music.groupby('item').count()['user']

music_subset = (music.set_index('user')
    .loc[user_counts >= 150]
    .reset_index()
    .set_index('item')
    .loc[item_counts >= 100]
    .reset_index()
    .pivot(index = 'user', columns = 'item', values = 'rating')
    )

counts = []
shape = 30
stride = 1
for col in range(0, len(music_subset.columns) - shape, stride):
    for row in range (0, len(music_subset) - shape, stride):
        subset = music_subset.iloc[row:row+shape, col:col+shape]
        hits = sum(subset.count())            
        counts.append([row,col, hits])
    
best_row = (pd.DataFrame(counts, columns = ['row', 'col', 'n'])    
    .sort_values('n', ascending = False)
    .head(1)
    )

row_index = best_row.iloc[0,0]
col_index = best_row.iloc[0,1]
my_subset = music_subset.iloc[row_index:row_index+30, col_index:col_index+30]  

long_df = (my_subset.reset_index()
    .melt(id_vars = 'user')
    )

train, test = train_test_split(long_df.dropna(), test_size = .3, random_state = 7)
train['is_train'] = 1
test['is_test'] = 1

full_df = long_df.join(train.is_train).join(test.is_test)


def calc_bias(df, column):
    df = df.copy()
    df[column + '_bias'] = df.value - df.rating_avg
    return df

train_final = full_df.loc[full_df.is_test != 1]

avg_rating = train_final.value.mean()
train_final['rating_avg'] = avg_rating

train_user = train_final.groupby('user').mean().pipe(calc_bias, 'user')
train_item = train_final.groupby('item').mean().pipe(calc_bias, 'item')


train_final = (train_final.join(train_item.item_bias, on = 'item')
    .join(train_user.user_bias, on = 'user')
)

def predict_val(df):
    raw_val = df.rating_avg - df.item_bias - df.user_bias
    return max(min(raw_val, 5), 0)

train_final['predicted'] = train_final.apply(lambda x: predict_val(x), axis = 1)

rmse = ((train_final.predicted- train_final.value) ** 2).mean()**.5

test_final = full_df.loc[full_df.is_test == 1]

test_final['rating_avg'] = avg_rating
test_final = (test_final.join(train_item.item_bias, on = 'item')
    .join(train_user.user_bias, on = 'user')
    .fillna(0)
)

test_final['predicted'] = test_final.apply(lambda x: predict_val(x), axis = 1)

rmse = ((test_final.predicted- test_final.value) ** 2).mean()**.5
