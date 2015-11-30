# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0002_functioncall'),
        ('enhance', '0006_similaritypair_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScriptTopic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('probability', models.FloatField()),
                ('script', models.ForeignKey(related_name='topic_probabilities', to='corpus.Script', db_index=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=200)),
                ('index', models.IntegerField()),
                ('alpha', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TopicDictToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token_index', models.IntegerField()),
                ('probability', models.FloatField()),
                ('token', models.ForeignKey(related_name='topic_scores', to='enhance.DictToken')),
                ('topic', models.ForeignKey(related_name='token_scores', to='enhance.Topic')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TopicModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=200)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('perplexity', models.FloatField(default=0)),
                ('dictionary', models.ForeignKey(to='enhance.Dictionary')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='topic',
            name='model',
            field=models.ForeignKey(related_name='topics', to='enhance.TopicModel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topic',
            name='scripts',
            field=models.ManyToManyField(related_name='topics', through='enhance.ScriptTopic', to='corpus.Script'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topic',
            name='tokens',
            field=models.ManyToManyField(related_name='topics', through='enhance.TopicDictToken', to='enhance.DictToken'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='scripttopic',
            name='topic',
            field=models.ForeignKey(related_name='script_probabilities', to='enhance.Topic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='scripttopic',
            name='topic_model',
            field=models.ForeignKey(to='enhance.TopicModel', db_index=False),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='scripttopic',
            index_together=set([('topic_model', 'script'), ('script', 'topic')]),
        ),
        migrations.AddField(
            model_name='tokenvectorelement',
            name='dictionary',
            field=models.ForeignKey(default=None, blank=True, to='enhance.Dictionary', null=True, db_index=False),
            preserve_default=True,
        ),
    ]
