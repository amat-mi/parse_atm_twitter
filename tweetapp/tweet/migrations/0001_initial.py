# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='tweet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo_tweet', models.BooleanField()),
                ('date', models.DateTimeField()),
                ('id_evento', models.IntegerField(null=True, blank=True)),
                ('tipo_evento', models.NullBooleanField()),
                ('linea', models.IntegerField(null=True, blank=True)),
                ('tweet', models.CharField(max_length=b'200')),
            ],
        ),
    ]
