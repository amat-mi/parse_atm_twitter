# -*- coding: utf-8 -*-
import tweepy
import json
import re
import unicodecsv as csv #import csv
import HTMLParser
import psycopg2
import sys

from twitter_keys import *


def tweet_to_csv(filename):
# TODO: use pandas to write a df

    ### import keys from twitter_keys.py ###
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)

    api = tweepy.API(auth)
    results = api.user_timeline()
    d={}
    a=[]
    for tweet in tweepy.Cursor(api.user_timeline, screen_name='@atm_informa', count=200, include_rts=True).items(200):
        d={}
        d['tweet']=tweet.text
        d['data']= tweet.created_at
        d['reply']=tweet.in_reply_to_screen_name
        a.append(d)
    c=[]
    for d in a :
        messages=tweet_interpreter(d['tweet'])
        for message in messages:
            message.update(d)
            c.append(message)
    ###http://www.gadzmo.com/python/reading-and-writing-csv-files-with-python-dictreader-and-dictwriter/
    f= open(,'wb')
    fieldnames = ('data', 'tweet', 'reply','linea','direzione','tipo_guasto','motivazione')
    csvwriter = csv.DictWriter(f,delimiter=';', fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
    csvwriter.writeheader()
    for row in c:
         if not row['reply']: ####  non scrive i tweet che hanno una risposta
            csvwriter.writerow(row)
    f.close



def tweet_interpreter (tweet):

    ###la linea non viene cercatata dopo gli ultimi ":" (in alcuni casi viene twittata una linea (non seguita dai :) es. sostitutiva
    str_line=tweet.rpartition(':')[0]

    linee = re.findall (r'(#bus\d+|#tram\d+|#M\d)', str_line)

    output=[]
    for i in linee:

        d={}
        ##### linea
        if re.search(r'M',i): ### se MM
            d['linea'] = re.search(r'\#(\w\d)',i).group(1) ### testo+numeri dopo # per MM
        else:
            d['linea'] = re.search(r'\d+',i).group() ### solo numeri per superficie
        ##########
        #### direzione (se esiste)
        if re.search (i+r'(\s*\>\s*(\w+))', tweet): ## se esiste un testo dopo >
            d['direzione'] = re.search(i+r'(\s*\>\s*(\w+))', tweet).group(2) ### direzione
        else:
            d['direzione']= 'no_direzione'
        ###########
        ##### tipo_guasto
        if re.search(r'riprend',tweet):
            d['tipo_guasto']= 'fine_guasto'
        else:
            if re.search(r'devi',tweet):
                d['tipo_guasto']= 'deviazione' ##### TODO deviazione da a
            if re.search(r'rall',tweet):
                d['tipo_guasto']= 'rallentamento'
            if re.search(r'interr',tweet):
                d['tipo_guasto']=  'interruzione'
            if re.search(r'term',tweet):
                d['tipo_guasto']=  'termina'##### TODO termina a, bus sostitutivo
                #print re.search(r'term\w+\s*(\w+)',tweet)

    ### motivazione (valdio se vale vale test_motivazione)
        if re.search(r'\((.*)\)', tweet):
            d['motivazione']= re.search(r'\((.*)\)', tweet).group(1)
        output.append(d)
    return output




filename ='/home/franco/workspace/amat/tweet/test.csv'
tweet_to_csv(filename)

#tweet_interpreter ("#bus50 #bus61: rallentamenti (traffico intenso in zona piazza Bol�var). #ATM #Milano")
#tweet_interpreter ("#tram16: termina in largo d�Ancona (inconveniente tecnico). Collegamento bus tra largo d�Ancona e piazzale Segesta. #ATM #Milano")
