# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0018_auto_20170306_0714'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiffTokenVectorElement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('frequency', models.IntegerField(default=0)),
                ('dic_token_index', models.IntegerField(default=0)),
                ('tfidf', models.FloatField(default=0.0)),
                ('dic_token', models.ForeignKey(related_name='diff_token_vector_elements', to='enhance.DictToken')),
                ('dictionary', models.ForeignKey(default=None, blank=True, to='enhance.Dictionary', null=True, db_index=False)),
                ('script_diff', models.ForeignKey(related_name='diff_token_vector_elements', to='enhance.ScriptDiff')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
