# parse_atm_twitter
run parse_twitter_streaming.py

tenere in locale il file twitter_keys.py con le chiavi di accesso così strutturato: consumer_key = '' consumer_secret = '' access_key = '' access_secret = ''

# Installazione in Ubuntu

Creare il file di configurazione per upstart:

    sudo pico /etc/init/parse_atm_twitter.conf
    
con il seguente contenuto:

    description "Parses and filters Tweets from ATM and send them to Django"

    start on runlevel [2345]
    stop on runlevel [!2345]

    respawn

    exec python /var/www/django/projects/parse_atm_twitter/parse_twitter_streaming.py

e attivare il servizio con il comando:

    sudo service parse_atm_twitter start


    
