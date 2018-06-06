# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from email.utils import parsedate_tz
import html
import json
import re
import sys

import pytz
import requests
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

from twitter_keys import *


def tweet_interpreter(dict_tweet):
    # TODO: verificare se necessario filtrare i twitter con reply !=0 per eliminare i tweet di risposta ad utenti #if not row['reply']
    # TODO: verificare se necessario filtrare i RT
    testo = dict_tweet['testo']    
    #normalizza con valori di default
    dict_tweet.setdefault('tipo',0)    
    dict_tweet.setdefault('stamp',datetime.now().isoformat())    
    ### estrae l'eventuale causa (Es: "(lavori stradali)") e la imposta, se non già presente
    ### se sono presenti più blocchi di testo tra parentesi, non imposta la causa
    ### NOOO!!! Se ci sono più blocchi, usiamo l'ultimo!!!
    cause = re.findall(r'\(([^\)]*)\)',testo)
#     causa = cause[0] if len(cause) == 1 else None 
    causa = cause[-1] if len(cause) >= 1 else None 
    dict_tweet.setdefault('causa',causa)    
    ### se un tweet inizia con un numero viene escluso perchè contiene info su date future
    if re.match(r'(\d)',testo[0]):
        return [dict_tweet]
    ### se un tweet ha l'hashtag #Milan viene escluso perchè è in inglese (non sempre il filtro sulla lingua funziona)
    if re.search(r'\bMilan\b',testo):
        return [dict_tweet]
    ### se un tweet non contiene almeno un ":", viene escluso
    before,sep,after = testo.partition(':')
    if not sep or not after:
        return [dict_tweet]
    ### prova ad estrarre dal testo prima dei ":" i riferimenti alle Linee
    linee = re.findall (r'(#bus\d+|#tram\d+|#M\d)', before)
    ### se un tweet non ha riferimenti alle Linee, viene escluso
    if not linee:
        return [dict_tweet]
    ### si deve creare un evento per ogni Linea alla quale il Tweet fa riferimento      
    interpreted_tweet=[]
    for linea in linee:
        d = {'stamp': dict_tweet['stamp'],
             'testo': dict_tweet['testo'],
             'causa': causa
             }
        #in codice Linea separa testo e numero e sostituisce con singolo carattere (Es: 'bus58'=>'B58')
        m = re.search(r'\#(\w+)(\d+)',linea)    
        d['linea'] = m.group(1).replace('bus','B').replace('tram','T') + m.group(2)            
        # tipo [0 = non evento, 1 = aperto, 2 = continuazione, 3 = chiuso]
        if re.search(r'riprend|prosegue',after):
            d['tipo'] = 3         #evento di Chiusura
        else:                 ### non è gestito l'evento continuazione: di default sono tutti di apertura = 1            
            d['tipo'] = 1         #evento di Apertura
        interpreted_tweet.append(d)
    return interpreted_tweet


def tweet_post(dict_tweet):
#     print(dict_tweet)
      #bisogna inviare ogni tweet separatamente, se sono più di uno
      tweets = [dict_tweet] if isinstance(dict_tweet,dict) else dict_tweet 
      for tweet in tweets: 
#           r = requests.post("http://127.0.0.1:8000/tweet/tweet/upload/", json=tweet)
          r = requests.post("https://dati.amat-mi.it/tweet/tweet/upload/", json=tweet)
          print(r.text)


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
        
        dict_data_filter={}
        dict_data_filter['tipo'] = 0
        dict_data_filter['testo'] = html.unescape(dict_data["text"])
        dict_data_filter['stamp'] = pytz.utc.localize(to_datetime(dict_data["created_at"])).isoformat()
        #d['user'] = dict_data["screen_name"]
        #dict_data_filter['reply_to'] = dict_data["in_reply_to_screen_name"]
        tweet_post(tweet_interpreter(dict_data_filter))

    # on failure
    def on_error(self, status):
        print(status)



if __name__ == '__main__':

    try:
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
  
      print('ok_user')
    except Exception as exc:
      print(str(exc))
 