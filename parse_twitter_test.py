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

    ### import keys from twitter_keys.py ###
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)

    api = tweepy.API(auth)
    results = api.user_timeline()
    h= HTMLParser.HTMLParser()
    d={}
    a=[]
    for tweet in tweepy.Cursor(api.user_timeline, user_id = '988355810', count=200, include_rts=True).items(200):
        d={}
        d['tweet'] = h.unescape(tweet.text)
        d['data'] = tweet.created_at
        d['reply'] = tweet.in_reply_to_screen_name
        d['lang'] = tweet.lang
        print d['reply']
        a.append(d)
    c=[]
    for d in a :
        messages = tweet_interpreter_route(d['tweet'])
        for message in messages:
            message.update(d)
            c.append(message)
    ###http://www.gadzmo.com/python/reading-and-writing-csv-files-with-python-dictreader-and-dictwriter/
    f= open(filename,'wb')
    fieldnames_all = ('data', 'tweet', 'reply','linea','direzione','tipo_guasto','motivazione')
    fieldnames_route = ('data','id_evento','tipo_evento','linea','tweet', 'reply','lang')
    csvwriter = csv.DictWriter(f,delimiter=';', fieldnames=fieldnames_route, quoting=csv.QUOTE_NONNUMERIC)
    csvwriter.writeheader()
    for row in c:
        # TODO: verificare cosa succede in caso di reply !=0
        #if not row['reply']: ####  non scrive i tweet che hanno una risposta
        if row['lang'] == 'it' :
            csvwriter.writerow(row)
    f.close


def tweet_interpreter_route (tweet):

    ### se un tweet inizia con un numero viene escluso perchè contiene info su date future
    if re.match(r'(\d)',tweet[0]):
        return []
    ### se un tweet ha l'hashtag #Milan viene escluso perchè è in inglese (non sempre il filtro sulla lingua funziona)
    if re.search(r'\bMilan\b',tweet):
        return []

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
        ##### tipo_evento [1 = aperto, 0 = chiuso]
        if re.search(r'riprend',tweet):
            d['tipo_evento']= 0
        else:
            d['tipo_evento']= 1
        output.append(d)

    return output





def tweet_interpreter (tweet):

    ###la linea non viene cercatata dopo gli ultimi ":" (in alcuni casi viene twittata una linea (non seguita dai :) es. sostitutiva
    str_line=tweet.rpartition(':')[0]

    linee = re.findall (r'(#bus\d+|#tram\d+|#M\d)', str_line)
    n_direction = re.findall (r'(>)', str_line)
    print n_direction

    output=[]
    for i in linee:
        print i

        d={}
        ##### linea
        if re.search(r'M',i): ### se MM
            d['linea'] = re.search(r'\#(\w\d)',i).group(1) ### testo+numeri dopo # per MM
        else:
            d['linea'] = re.search(r'\d+',i).group() ### solo numeri per superficie
        ##########
        #### direzione (se esiste)
        if re.search(i+r'(.*?)\s*\:',tweet):## se esiste un testo dopo >
            d['direzione'] = re.search(i+r'(.*?)\s*\:',tweet).group(1) ### direzione
            print re.search(i+r'(.*?)\s*\:',tweet).group(1)
        #if re.search (i+r'(\s*\>\s*(\w+))', tweet): ## se esiste un testo dopo >
        #    d['direzione'] = re.search(i+r'(\s*\>\s*(\w+))', tweet).group(2) ### direzione



#re.search(r'[\w.-]+@[\w.-]+', str)

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




filename ='/home/franco/workspace/amat/tweet/tweet_route.csv'
tweet_to_csv(filename)

#tweet_interpreter ("#bus47 #bus74 #bus325 > Cantore: riprendono il percorso regolare dopo deviazione per urto tra mezzi privati. #ATM #Milano")
#tweet_interpreter ("#tram14 > Lorenteggio: riprende il percorso regolare, > Cimitero Maggiore: devia da Coni Zugna a Orefici (incidente). #ATM #Milano")
