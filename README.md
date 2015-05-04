# parse_atm_twitter
run parse_twitter_streaming.py

tenere in locale il file twitter_keys.py con le chiavi di accesso così strutturato: consumer_key = '' consumer_secret = '' access_key = '' access_secret = ''

# Installazione in Ubuntu

Installare il file di configurazione per upstart:

    sudo cp parse_atm_twitter.conf /etc/init/
    sudo chown root.root /etc/init/parse_atm_twitter.conf
    sudo chmod u=rw,go=r /etc/init/parse_atm_twitter.conf
    
e attivare il servizio con il comando:

    sudo initctl start parse_atm_twitter
    
Il log è visibile con il comando:

     sudo cat /var/log/upstart/parse_atm_twitter.log
     


    
