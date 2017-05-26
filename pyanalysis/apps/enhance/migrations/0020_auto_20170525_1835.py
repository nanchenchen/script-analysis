# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0019_difftokenvectorelement'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScriptDiffTopic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('probability', models.FloatField()),
                ('script_diff', models.ForeignKey(related_name='diff_topic_probabilities', to='enhance.ScriptDiff', db_index=False)),
                ('topic', models.ForeignKey(related_name='script_diff_probabilities', to='enhance.Topic')),
                ('topic_model', models.ForeignKey(to='enhance.TopicModel', db_index=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='scriptdifftopic',
            index_together=set([('topic_model', 'script_diff'), ('script_diff', 'topic')]),
        ),
    ]
