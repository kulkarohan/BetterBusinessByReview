from flask import Flask, render_template, flash
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField
from wtforms import TextField, HiddenField, ValidationError, RadioField,\
    BooleanField, SubmitField, IntegerField, FormField, validators
from wtforms.validators import Required

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
from flask import Response
from spacy.tokenizer import Tokenizer
warnings.filterwarnings('ignore')


# straight from the wtforms docs:
class TelephoneForm(FlaskForm):
    country_code = IntegerField('Country Code', [validators.required()])
    area_code = IntegerField('Area Code/Exchange', [validators.required()])
    number = TextField('Number')


class ExampleForm(FlaskForm):
    field1 = TextField('First Field', description='This is field one.')
    # field2 = TextField('Second Field', description='This is field two.',
    #                    validators=[Required()])
    # hidden_field = HiddenField('You cannot see this', description='Nope')
    # recaptcha = RecaptchaField('A sample recaptcha field')
    # radio_field = RadioField('This is a radio field', choices=[
    #     ('head_radio', 'Head radio'),
    #     ('radio_76fm', "Radio '76 FM"),
    #     ('lips_106', 'Lips 106'),
    #     ('wctr', 'WCTR'),
    # ])
    # checkbox_field = BooleanField('This is a checkbox',
    #                               description='Checkboxes can be tricky.')
    #
    # # subforms
    # mobile_phone = FormField(TelephoneForm)
    #
    # # you can change the label as well
    # office_phone = FormField(TelephoneForm, label='Your office phone')
    #
    # ff = FileField('Sample upload')

    submit_button = SubmitField('Submit')


    def validate_hidden_field(form, field):
        raise ValidationError('Always wrong')




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
    df.columns = ['date','review','rating']

    df = df.set_index(df.columns.drop('review',1).tolist()).review.str.split('.', expand=True).stack().reset_index().rename(columns={0:'review'}).loc[:, df.columns]

    df = df.replace(',','')
    df = df.replace('!','')
    df = df.replace('#','')
    df = df.replace('.','')
    tokenizer = Tokenizer(nlp.vocab)
    STOP_WORDS =nlp.Defaults.stop_words.union(['gets','incredible','disappoint','from','perfection','loved','definitely','happy','find','found','simply','fantastic','recommend','feel','little','i','wow','absolute','favorite','excellent','delicious','great','maybe','very','enjoy','list','gave','date','went','disappointed','nyc','got','#','crazy','other','fairness','fair','mid','from','highly','perfect','perfectly','come','lovely','visit','ny','nyc','best','amazing','love','absolutely','like','good','other','from','ny','restaurant','we','will','because','not','friends','amazing','awesome','first','he','check-in','=','= =','male','u','want', 'u want', 'cuz','him',"i've", 'deaf','on', 'her','told','told him','ins', 'check-ins','check-in','check','I', 'i"m', 'i', 'it', "it's", 'it.','they','coffee','place','they', 'the', 'this','its', 'l','-','they','this','don"t','the ',' the', 'it', 'i"ve', 'i"m', '!', '1','2','3','4', '5','6','7','8','9','0','(',')','/','.',',','!'])
# STOP_WORDS
    df = df[df['review'] !=None]
    tokens = []

    for doc in tokenizer.pipe(df['review'], batch_size=500):

        doc_tokens = []

        for token in doc: 
            if (token.text not in STOP_WORDS) & (token.is_punct == False):
                doc_tokens.append(token.text.lower())
        tokens.append(doc_tokens)

    df['review'] = tokens
    jointty = lambda x: ' '.join(map(lambda x: str(x), x['review']))
    df['review'] = df.apply(jointty, axis=1)
    df['review'].replace(' ', np.nan, inplace=True)
    df= df.dropna()

    corpus = (st.CorpusFromPandas(df,
                             category_col='rating',
                             text_col='review',
                             nlp=nlp).build().remove_terms(STOP_WORDS, ignore_absences=True))

    term_freq_df = corpus.get_term_freq_df()
    term_freq_df['highratingscore'] = corpus.get_scaled_f_scores('5.0 star rating')

    term_freq_df['poorratingscore'] = corpus.get_scaled_f_scores('1.0 star rating')
    # term_freq_df = term_freq_df[term_freq_df['1.0 star rating freq'] > 3]
    dp = term_freq_df.sort_values(by= 'poorratingscore', ascending = False)
    dp = dp[~dp.index.str.contains('-')]
    dp = dp[~dp.index.str.contains("'")]
    dp = dp[~dp.index.str.contains('/')]
    dh = term_freq_df.sort_values(by= 'highratingscore', ascending = False)
    dh = dh[~dh.index.str.contains('-')]
    dh = dh[~dh.index.str.contains("'")]
    dh = dh[~dh.index.str.contains('/')]
    dhi = dh.head(75)
    dpo = dh.tail(75)
    dfinal = pd.concat([dhi,dpo])
    # dh = dh.reset_index(drop=False)

    # return dh.to_dict('index')
    return dfinal.to_dict('index')


#app
app=Flask(__name__)
CORS(app)


def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)  # Flask-Appconfig is not necessary, but
                                # highly recommend =)
                                # https://github.com/mbr/flask-appconfig
    Bootstrap(app)

    # in a real app, these should be configured through Flask-Appconfig
    app.config['SECRET_KEY'] = 'devkey'
    app.config['RECAPTCHA_PUBLIC_KEY'] = \
        '6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'

    @app.route('/', methods=('GET', 'POST'))
    def index():
        form = ExampleForm()
        form.validate_on_submit()  # to get error messages to the browser
        # flash('critical message', 'critical')
        # flash('error message', 'error')
        # flash('warning message', 'warning')
        # flash('info message', 'info')
        # flash('debug message', 'debug')
        # flash('different message', 'different')
        # flash('uncategorized message')
        return render_template('index.html', form=form)

    @app.route('/result', methods=['POST'])
    def result():  # will capture our predictions, handles result
        #     content_type = request.headers["content-type"]
        #     if content_type == "application/json":
        if request.method == 'POST':
            to_predict_list = request.values['yelp_url']
            result = ValuePredictor(to_predict_list)
            return render_template("result.html", prediction=result)
            # return Response(json.dumps(result),  mimetype='application/json')
            #         return jsonify(test)

            
#             response = app.response_class(
#                 response=json.dumps(result),
#                 status=200,
#                 mimetype='application/json')

#             return render_template("results.html", prediction=result)
#     @app.route('/result', methods=['POST'])
#     def resultpage():  # will capture our predictions, handles result
#         if request.method == 'POST':
#             to_predict_list = request.values['yelp_url']
#             results = ValuePredictor(to_predict_list)
#             return render_template("results.html", prediction=results)
                

    @app.route('/about')
    def aboutpage():

        title = "About this site"
        paragraph = ["blah blah blah memememememmeme blah blah memememe"]

        pageType = 'about'

        return render_template("index.html", title=title, paragraph=paragraph, pageType=pageType)

    @app.route('/about/contact')
    def contactPage():

        title = "About this site"
        paragraph = ["blah blah blah memememememmeme blah blah memememe"]

        pageType = 'about'

        return render_template("index.html", title=title, paragraph=paragraph, pageType=pageType)

    return app






#app run
if __name__ == '__main__':
    create_app().run(host='0.0.0.0')
