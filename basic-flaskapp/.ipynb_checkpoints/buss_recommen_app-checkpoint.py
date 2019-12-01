import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.tree import DecisionTreeClassifier

import pickle
import json
import requests

shops = pd.read_csv('C:\\Users\\lilyx\\DS-Unit-4-Sprint-1-NLP\\module1-text-data\\data\\yelp_coffeeshop_review_data.csv')

#to remove dates at the beginning of string, split the string into a list of words, then indexing the second to last words
splitty = lambda x: x['full_review_text'].split()[1:]
shops['full_review_text'] = shops.apply(splitty, axis=1)

#join list of words back together
jointty = lambda x: ' '.join(map(lambda x: str(x), x['full_review_text']))
shops['full_review_text'] = shops.apply(jointty, axis=1)

#lowercasing all words in review
lowercase = lambda x: str.lower(x['full_review_text'])
shops['full_review_text'] = shops.apply(lowercase, axis=1)

#calling spacy's default stop words and adding some manually
nlp = spacy.load("en_core_web_md")
tokenizer = Tokenizer(nlp.vocab)#breaks text, it creates character indexes instead of splitting words up

STOP_WORDS = nlp.Defaults.stop_words.union(['check-in','him',"i've", 'deaf','on', 'her','told','told him','ins',
                                     '1 check','I', 'i"m', 'i', ' ', 'it', "it's", 'it.','they','coffee','place',
                                     'they', 'the', 'this','its', 'l','-','they','this','don"t','the ', ' the', 
                                     'it', 'i"ve', 'i"m', '!', '1','2','3','4', '5','6','7','8','9','0','/','.',
                                     ','])

#create tokens based on stop words
tokens = []

for doc in tokenizer.pipe(shops['full_review_text'], batch_size=800):
    
    doc_tokens = []
    
    for token in doc: 
        if token.text not in STOP_WORDS:
            doc_tokens.append(token.text.lower())
   
    tokens.append(doc_tokens)
    
shops['tokens'] = tokens

#join tokens back together for use
jointty = lambda x: ' '.join(map(lambda x: str(x), x['tokens']))
shops['joined_tokens'] = shops.apply(jointty, axis=1)

#start of scattertext library magic
corpus = st.CorpusFromPandas(shops, 
                             category_col='star_rating', 
                             text_col='joined_tokens',
                             nlp=nlp).build()

#getting a list of words correlated with high rating score
term_freq_df = corpus.get_term_freq_df()
term_freq_df['highratingscore'] = corpus.get_scaled_f_scores(' 5.0 star rating ')
pprint(list(term_freq_df.sort_values(by='highratingscore', ascending=False).index[:10]))

#getting a list of words correlated with low rating score
term_freq_df['poorratingscore'] = corpus.get_scaled_f_scores(' 1.0 star rating ')
pprint(list(term_freq_df.sort_values(by='poorratingscore', ascending=False).index[:10]))

#creating a dataframe ranking the words correlated with poorest ratings
term_freq_df.sort_values(by= 'poorratingscore', ascending = False)

html = st.produce_scattertext_explorer(corpus,
         category=' 1.0 star rating ',
         category_name='Poor Yelp Rating',
         not_category_name='High Yelp Rating',
         width_in_pixels=1000,
         metadata=shops['coffee_shop_name'])

         
open("Yelp-CoffeeShop-Visualization.html", 'wb').write(html.encode('utf-8'))