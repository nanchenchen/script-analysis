# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0015_auto_20160629_0615'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScriptDiff',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(default=b'', null=True, blank=True)),
                ('pair', models.ForeignKey(related_name='diff', to='enhance.SimilarityPair')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
