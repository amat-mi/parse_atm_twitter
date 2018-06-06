# parse_atm_twitter

# Installazione

Tenere in locale il file local_secrets.py con le chiavi di accesso così strutturato:

```
# -*- coding: utf-8 -*-

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
TWITTER_ACCESS_KEY = ''
TWITTER_ACCESS_SECRET = ''
AMAT_TWEET_SERVER_URL = ''
AMAT_TWEET_SERVER_TOKEN = ''
```

## Windows

Creare un virtualenv con python3, per esempio:

    virtualenv3 c:\Users\Paolo\venv\parse_atm_twitter
    
## Ubuntu

Creare virtual env per il progetto:
	
    virtualenv /var/www/django/venv/parse_atm_twitter

Clonare i repository necessari:

    cd /var/www/django/projects
    git clone https://github.com/amat-mi/parse_atm_twitter.git
    
__ATTENZIONE!!!__ Se necessario fare git switchout sul branch opportuno!!!

Attivare il virtualenv ed installare i requirements:

    . /var/www/django/venv/parse_atm_twitter/bin/activate
    cd /var/www/django/projects/parse_atm_twitter
    pip install -r requirements.txt
    deactivate

## Ubuntu <15.10 (using upstart)

Installare il file di configurazione per upstart:

    sudo cp parse_atm_twitter.conf /etc/init/
    sudo chown root.root /etc/init/parse_atm_twitter.conf
    sudo chmod u=rw,go=r /etc/init/parse_atm_twitter.conf
    
e attivare il servizio con il comando:

    sudo initctl start parse_atm_twitter
    
Il log è visibile con il comando:

     sudo cat /var/log/upstart/parse_atm_twitter.log

## Systemd (per Ubuntu >= 15.02 che usa systemd)

Installare il file di configurazione per systemd:

    sudo cp parse_atm_twitter.service /etc/systemd/system/
    sudo chown root.root /etc/systemd/system/parse_atm_twitter.service
    sudo chmod u=rw,go=r /etc/systemd/system/parse_atm_twitter.service

Abilitare e far partire il servizio:

    sudo systemctl enable parse_atm_twitter.service
    sudo systemctl start parse_atm_twitter.service

Per verificare lo stato del servizio:
    
    sudo systemctl status parse_atm_twitter.service

ATTENZIONE!!! Se si modifica il file di configurazione, è necessario aggiornarlo con i comandi:

    sudo systemctl daemon-reload
    sudo systemctl restart parse_atm_twitter.service

Notare che è possibile usare anche i consueti comandi "service", che sono mappati su quelli di systemd.
     