# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0002_functioncall'),
        ('enhance', '0011_tokenvectorelement_line'),
    ]

    operations = [
        migrations.CreateModel(
            name='DifferenceNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.TextField(default=b'', blank=True)),
                ('src_script', models.ForeignKey(related_name='difference_notes', to='corpus.Script')),
                ('tar_script', models.ForeignKey(to='corpus.Script')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='differencenote',
            index_together=set([('src_script', 'tar_script')]),
        ),
    ]
