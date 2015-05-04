# -*- coding: utf-8 -*-

import HTMLParser
import json
import re
import sys

from email.utils import parsedate_tz
from datetime import datetime, timedelta
import pytz

import requests
from textblob import TextBlob
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

from twitter_keys import *
import unicodecsv as csv


# import twitter keys and tokens
filename = '/home/franco/workspace/amat/tweet/tweet_route.csv'


def tweet_interpreter(dict_tweet):
#     print dict_tweet

    # in questo punto è possibile inserire filtri
    # TODO: verificare se necezzario filtrare i twitter con reply !=0 per eliminare i tweet di risposta ad utenti #if not row['reply']
    # TODO: verificare se necezzario filtrare i RT
    # isolo il testo del twitter per interpretarlo
    tweet = dict_tweet['testo']
    # se un tweet inizia con un numero viene escluso perchè contiene info su date future
    not_interpreted_tweet=[]
    if re.match(r'(\d)',tweet[0]):
        not_interpreted_tweet.append(dict_tweet)
        return not_interpreted_tweet
    # se un tweet ha l'hashtag #Milan viene escluso perchè è in inglese (non sempre il filtro sulla lingua funziona)
    if re.search(r'\bMilan\b',tweet):
        not_interpreted_tweet.append(dict_tweet)
        return not_interpreted_tweet
    # la linea non viene cercatata dopo gli ultimi ":" (in alcuni casi viene twittata una linea (non seguita dai :) es. sostitutiva
    str_line = tweet.rpartition(':')[0]
    linee = re.findall (r'(#bus\d+|#tram\d+|#M\d)', str_line)
    if linee:
        interpreted_tweet=[]
        # crea un dizionario per ogni linea
        for i in linee:
            d={}
            # linea
            if re.search(r'M',i): # se MM
                d['linea'] = re.search(r'\#(\w\d)',i).group(1) # testo+numeri dopo # per MM
            else:
                d['linea'] = re.search(r'\d+',i).group() # solo numeri per superficie
            # tipo [0 = non evento, 1 = aperto, 2 = continuazione, 3 = chiuso]
            if re.search(r'riprend|prosegue',tweet):
                d['tipo'] = 3
            else:
                ### non è gestito l'evento continuazione: di default sono tutti di apertura = 1
                d['tipo'] = 1
            d['stamp'] = dict_tweet['stamp']
            d['testo'] = dict_tweet['testo']
            interpreted_tweet.append(d)
        return interpreted_tweet
    else:
        not_interpreted_tweet.append(dict_tweet)
        return not_interpreted_tweet


def tweet_post(dict_tweet):
#     print dict_tweet
#       r = requests.put("http://127.0.0.1:8000/tweet/tweet/upload/", json=dict_tweet)
      r = requests.put("http://dati.amat-mi.it/tweet/tweet/upload/", json=dict_tweet)
      print r.text

def tweet_write_file(dict_tweet,filename):

    #TODO : scrivere l'head una sola volta
    with open(filename,'a') as f:
        fieldnames = ('data','id_evento','tipo','linea','tweet')
        csvwriter = csv.DictWriter(f, delimiter=';', fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
        csvwriter.writeheader()
        for row in dict_tweet:
            csvwriter.writerow(row)
        f.close


def to_datetime(datestring):
    time_tuple = parsedate_tz(datestring.strip())
    dt = datetime(*time_tuple[:6])
    return dt - timedelta(seconds=time_tuple[-1])


class TweetStreamListener(StreamListener):

    # on success
    def on_data(self, data):
        # decode json
        dict_data = json.loads(data)
        # filter retweet
        if  dict_data.get ('retweeted_status', None) is not None:
            return
        # filter reply to
        if dict_data.get ('in_reply_to_screen_name', None) is not None:
            return
        # TODO filter on dict_data using underscore
        
        h= HTMLParser.HTMLParser()
        dict_data_filter={}
        dict_data_filter['tipo'] = 0
        dict_data_filter['testo'] = h.unescape(dict_data["text"])
        dict_data_filter['stamp'] = pytz.utc.localize(to_datetime(dict_data["created_at"])).isoformat()
        #d['user'] = dict_data["screen_name"]
        #dict_data_filter['reply_to'] = dict_data["in_reply_to_screen_name"]
        #tweet_write_file(tweet_interpreter(dict_data_filter),filename)
        tweet_post(tweet_interpreter(dict_data_filter))

    # on failure
    def on_error(self, status):
        print status



if __name__ == '__main__':

    if len(sys.argv) > 1:
        dict_data_filter={}
        dict_data_filter['testo'] = sys.argv[1]
        dict_data_filter['stamp'] = datetime.now().isoformat()
        tweet_post(tweet_interpreter(dict_data_filter))
        sys.exit()

    # create instance of the tweepy tweet stream listener
    listener = TweetStreamListener()
    # set twitter keys/tokens
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)

    # create instance of the tweepy stream
    stream = Stream(auth, listener)

    #use for test:
    #stream.filter(track=['congress'])

    # search twitter for "@atm_informa" user
#     stream.filter(follow = ['988355810'], languages = ['it'])

    # search twitter for "@testsforapp" user
#     stream.filter(follow = ['2768232307'], languages = ['it'])

    # search both twitter for "@atm_informa" user and "@testsforapp" user
    stream.filter(follow = ['988355810','2768232307'], languages = ['it'])

    # search twitter for "@testsforapp" user
#     stream.filter(follow = ['2768232307'], languages = ['it'])

    print 'ok_user'
