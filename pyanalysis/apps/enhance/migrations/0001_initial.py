# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pyanalysis.apps.enhance.fields


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dictionary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('num_docs', pyanalysis.apps.enhance.fields.PositiveBigIntegerField(default=0)),
                ('num_pos', pyanalysis.apps.enhance.fields.PositiveBigIntegerField(default=0)),
                ('num_nnz', pyanalysis.apps.enhance.fields.PositiveBigIntegerField(default=0)),
                ('dataset', models.ForeignKey(related_name='dictionary', default=None, blank=True, to='corpus.Dataset', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DictToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', models.IntegerField()),
                ('text', models.CharField(max_length=256)),
                ('document_frequency', models.IntegerField()),
                ('dictionary', models.ForeignKey(related_name='dic_tokens', to='enhance.Dictionary')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TokenVectorElement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('frequency', models.IntegerField(default=0)),
                ('dic_token_index', models.IntegerField(default=0)),
                ('tfidf', models.FloatField(default=0.0)),
                ('dic_token', models.ForeignKey(related_name='token_vector_elements', to='enhance.DictToken')),
                ('script', models.ForeignKey(related_name='token_vector_elements', to='corpus.Script')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='dicttoken',
            name='scripts',
            field=models.ManyToManyField(related_name='dic_tokens', through='enhance.TokenVectorElement', to='corpus.Script'),
            preserve_default=True,
        ),
    ]
