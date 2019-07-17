# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 22:37:58 2019

@author: pgood
"""

import pandas as pd
import requests
import re
import pickle
import time

books = (pd.read_csv('https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/books.csv')
    .dropna(subset = ['language_code'])
)

eng_langs = ['en-US', 'en-CA', 'eng', 'en-GB', 'en']
books = books.loc[books.language_code.str.contains('en')]

def fix_title(title):
    test_var = re.search('[(]', title)
    if test_var:
        str_end = test_var.start()
        title = title[:str_end]
    return title

books['new_title'] = books['title'].map(fix_title)

all_descs = []
all_data = []
all_extracts = []
bad_books = []

search_endpoint = 'https://en.wikipedia.org/w/api.php'
params_search = {'action' : 'query','format': 'json', 'list' : 'search', 'srlimit': 5}
params_query = {'action' : 'query','format': 'json', 'prop' : 'extracts', 
                'exintro': '', 'explaintext': '', 'redirects' : 1
}
headers = {'User-Agent': 'pgoodridge2007@gmail.com'}

for _, row in books.iterrows():
    book = row.new_title 
    book_id = row.book_id
    
    if len(book.split()) <= 5:
        params_search['srsearch'] =  book + '%20novel' 
    else:
        params_search['srsearch'] =  book

    try:
        json_data = requests.get(search_endpoint, params = params_search, headers = headers).json()
        """
        #This makes the data a little more accurate but is slow
        for i in range(params['srlimit']):
            
            snip = json_data['query']['search'][i]['snippet']
            if snip.find('novel') > -1 or snip.find('book') > -1:
                page_title = json_data['query']['search'][i]['title']
                break
        """
        page_title = json_data['query']['search'][0]['title']
        params_query['titles'] = page_title
        query_data = requests.get(search_endpoint, params = params_query, headers = headers).json()
        page = query_data['query']['pages'].keys()
        for k in query_data['query']['pages'].keys():
            extract = query_data['query']['pages'][k]['extract']    
        all_extracts.append({book_id : extract})
        all_descs.append(json_data)
        all_data.append(query_data)
    except:
        bad_books.append(book_id)

"""
pickle.dump(all_descs, open( r"C:\Pickle files\all_descs.p", "wb" ))
pickle.dump(all_data, open( r"C:\Pickle files\all_data.p", "wb" ))
pickle.dump(all_extracts, open( r"C:\Pickle files\all_extracts.p", "wb" ))

row_tuples = [(k,v) for item in all_extracts for k, v in item.items()]

extracts_frame = pd.DataFrame(row_tuples, columns = ['book_id', 'desc'])

extracts_frame.to_csv('book_extracts.csv', index = False)
"""