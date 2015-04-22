from django.db import models

# Create your models here.


class tweet (models.Model):
    tipo_tweet = models.BooleanField(null=False,blank=False)
    date = models.DateTimeField(auto_now=False)
    id_evento = models.IntegerField(null=True,blank=True)
    tipo_evento = models.NullBooleanField(null=True,blank=True)
    linea = models.IntegerField(null=True,blank=True)
    tweet = models.CharField(max_length='200', null=False,blank=False)
