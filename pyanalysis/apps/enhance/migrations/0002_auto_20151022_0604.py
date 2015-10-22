# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tokenvectorelement',
            name='dic_token_index',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tokenvectorelement',
            name='tfidf',
            field=models.FloatField(default=0.0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tokenvectorelement',
            name='frequency',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
