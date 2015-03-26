# -*- coding: utf-8 -*-

import json
import unicodecsv as csv
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
import HTMLParser
import re


# import twitter keys and tokens
from twitter_keys import *

filename = '/home/franco/workspace/amat/tweet/tweet_route.csv'


def tweet_interpreter(dict_tweet,id):

    # in questo punto è possibile inserire filtri
    # TODO: verificare se necezzario filtrare i twitter con reply !=0 per eliminare i tweet di risposta ad utenti #if not row['reply']
    # TODO: verificare se necezzario filtrare i RT


    # isolo il testo del twitter per interpretarlo
    tweet = dict_tweet['tweet']
    # se un tweet inizia con un numero viene escluso perchè contiene info su date future
    if re.match(r'(\d)',tweet[0]):
        return []
    # se un tweet ha l'hashtag #Milan viene escluso perchè è in inglese (non sempre il filtro sulla lingua funziona)
    if re.search(r'\bMilan\b',tweet):
        return []
    # la linea non viene cercatata dopo gli ultimi ":" (in alcuni casi viene twittata una linea (non seguita dai :) es. sostitutiva
    str_line = tweet.rpartition(':')[0]
    linee = re.findall (r'(#bus\d+|#tram\d+|#M\d)', str_line)
    interpreted_tweet=[]
    # crea un dizionario per ogni linea
    for i in linee:
        d={}
        # linea
        if re.search(r'M',i): # se MM
            d['linea'] = re.search(r'\#(\w\d)',i).group(1) # testo+numeri dopo # per MM
        else:
            d['linea'] = re.search(r'\d+',i).group() # solo numeri per superficie
        # tipo_evento [1 = aperto, 0 = chiuso]
        if re.search(r'riprend',tweet):
            d['tipo_evento'] = 0
        else:
            d['tipo_evento'] = 1
        d['data'] = dict_tweet['data']
        interpreted_tweet.append(d)
    return interpreted_tweet

def tweet_interpreter_test(dict_tweet):
    d={}
    d['linea'] = dict_tweet['tweet']
    interpreted_tweet=[]
    interpreted_tweet.append(d)
    return interpreted_tweet



def tweet_write_file(dict_tweet,filename):

    #TODO : scrivere l'head una sola volta
    with open(filename,'a') as f:
        fieldnames = ('data','id_evento','tipo_evento','linea','tweet', 'reply_to')
        csvwriter = csv.DictWriter(f,delimiter=';', fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
        csvwriter.writeheader()
        for row in dict_tweet:
            csvwriter.writerow(row)
        f.close



class TweetStreamListener(StreamListener):

    # on success
    def on_data(self, data):
        h= HTMLParser.HTMLParser()
        # decode json
        dict_data = json.loads(data)
        # TODO filter on dict_data using underscore
        dict_data_filter={}
        dict_data_filter['tweet'] = dict_data[h.unescape("text")]
        dict_data_filter['data'] = dict_data["created_at"]
        #d['user'] = dict_data["screen_name"]
        dict_data_filter['reply_to'] = dict_data["in_reply_to_screen_name"]
        print dict_data_filter


        # write to file


        tweet_write_file(tweet_interpreter_test(dict_data_filter),filename)



    # on failure
    def on_error(self, status):
        print status





if __name__ == '__main__':


    # create instance of the tweepy tweet stream listener
    listener = TweetStreamListener()

    # set twitter keys/tokens
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)

    # create instance of the tweepy stream
    stream = Stream(auth, listener)

    #print tweet_interpreter('#bus54 #bus60 #bus61 #bus73 #busX73 #bus94: possibili deviazioni e rallentamenti (manifestazione in zona p.za San Babila). #ATM #Milano')
    #print tweet_interpreter ({'reply_to': 'atm_informa', 'tweet': '#bus54 #bus60 #bus61 #bus73 #busX73 #bus94: possibili deviazioni e rallentamenti (manifestazione in zona p.za San Babila). #ATM #Milano', 'data': 'Wed Mar 25 16:39:31'})
    # search twitter for "@atm_informa" user
    #stream.filter(follow = ['988355810'], languages = ['it'])
    stream.filter(track=['congress'])
