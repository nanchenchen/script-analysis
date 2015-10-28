# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0001_initial'),
        ('enhance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SimilarityPair',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('similarity', models.FloatField(default=0.0)),
                ('src_script', models.ForeignKey(related_name='similarity_pairs', to='corpus.Script')),
                ('tar_script', models.ForeignKey(to='corpus.Script')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
