import os
import numpy as np
import flask
import pickle
from flask import Flask, render_template, request, jsonify
import json
import os
import tarfile
import warnings
import numpy as np
import pandas as pd
import requests
import spacy
import wget
from spacy.lang.en import English
import scattertext as st
from json import loads
from lxml import html
from requests import Session
from concurrent.futures import ThreadPoolExecutor as Executor
from itertools import count
from flask import jsonify
import requests
from flask_cors import CORS
warnings.filterwarnings('ignore')

nlp = spacy.load("./down_sm/en_core_web_sm-2.1.0/en_core_web_sm/en_core_web_sm-2.1.0")

def ValuePredictor(yelp_url, from_isbn=False):
    '''Takes a url, scrape site for reviews
    and calculates the term frequencies 
    sorts and returns the top 10 as a json object
    containing term, highratingscore, poorratingscore.'''

    base_url = "https://www.yelp.com/biz/" # add business id
    api_url = "/review_feed?sort_by=date_desc&start="
    bid = yelp_url.replace('https://www.yelp.com/biz/','')
    if '?' in yelp_url:#deletes everything after "?" in url 
        bid = yelp_url.split('?')[0]

    class Scraper():
        def __init__(self):
            self.data = pd.DataFrame()

        def get_data(self, n, bid=bid):
            with Session() as s:
                with s.get(base_url+bid+api_url+str(n*20)) as resp: #makes an http get request to given url and returns response as json
                    r = dict(resp.json()) #converts json response into a dictionary
                    _html = html.fromstring(r['review_list']) #loads from dictionary

                    dates = _html.xpath("//div[@class='review-content']/descendant::span[@class='rating-qualifier']/text()")
                    reviews = [el.text for el in _html.xpath("//div[@class='review-content']/p")]
                    ratings = _html.xpath("//div[@class='review-content']/descendant::div[@class='biz-rating__stars']/div/@title")

                    df = pd.DataFrame([dates, reviews, ratings]).T

                    self.data = pd.concat([self.data,df])

        def scrape(self): #makes it faster
            # multithreaded looping
            with Executor(max_workers=40) as e:
                list(e.map(self.get_data, range(10)))

    s = Scraper()
    s.scrape()
    df = s.data#converts scraped data into 

    nlp.Defaults.stop_words |= {'will','because','not','friends','amazing','awesome','first','he','check-in','=','= =','male','u','want', 'u want', 'cuz','him',"i've", 'deaf','on', 'her','told','told him','ins', 'check-ins','check-in','check','I', 'i"m', 'i', ' ', 'it', "it's", 'it.','they','coffee','place','they', 'the', 'this','its', 'l','-','they','this','don"t','the ', ' the', 'it', 'i"ve', 'i"m', '!', '1','2','3','4', '5','6','7','8','9','0','/','.',','}

    corpus = st.CorpusFromPandas(df, 
                             category_col=2, 
                             text_col=1,
                             nlp=nlp).build()

    term_freq_df = corpus.get_term_freq_df()
    term_freq_df['highratingscore'] = corpus.get_scaled_f_scores('5.0 star rating')

    term_freq_df['poorratingscore'] = corpus.get_scaled_f_scores('1.0 star rating')
    dp = term_freq_df.sort_values(by= 'poorratingscore', ascending = False)
#     for i in dp.index: 
#         if ' ' in i:
#             dp = dp.drop([i])
    df = term_freq_df.sort_values(by= 'highratingscore', ascending = False)
#     for i in df.index: 
#         if ' ' in i:
#             df = df.drop([i])
    df = df[['highratingscore', 'poorratingscore']]

    df['highratingscore'] = round(df['highratingscore'], 2)
    df['poorratingscore'] = round(df['poorratingscore'], 2)
    df = df.reset_index(drop=False)
    df = df.head(5)

    dp = dp[['highratingscore', 'poorratingscore']]
    dp['highratingscore'] = round(dp['highratingscore'], 2)
    dp['poorratingscore'] = round(dp['poorratingscore'], 2)
    dp = dp.reset_index(drop=False)
    dp = dp.head(5)
    df = pd.concat([df,dp])
    return df.to_dict('records')


#app
app=Flask(__name__)
CORS(app)


#routes
@app.route('/')#defaults to this just in case, legacy reasons
@app.route('/index')
def index():
    return flask.render_template('index.html')#we are going to have a form

#hold and run the results page
@app.route('/result', methods = ['POST'])
def result():#will capture our predictions, handles result
#     content_type = request.headers["content-type"]
#     if content_type == "application/json":
    if request.method == 'POST':
        to_predict_list = request.values['yelp_url']
        result = ValuePredictor(to_predict_list)
    #         return jsonify(test)

        response = app.response_class(
            response=json.dumps(result),
            status=200,
            mimetype='application/json')

        return response
#     else:
#         return jsonify("Content-Type is not application/json")

#app run
if __name__ == '__main__':
    app.run(port=9000, debug=True)