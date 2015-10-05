# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Line',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField(default=0)),
                ('text', models.TextField(default=b'', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('last_modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('dataset', models.ForeignKey(related_name='scripts', to='corpus.Dataset')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('st_col', models.IntegerField(default=0)),
                ('ed_col', models.IntegerField(default=0)),
                ('type', models.CharField(default=b'', max_length=32, null=True, blank=True)),
                ('text', models.TextField(default=b'', null=True, blank=True)),
                ('line', models.ForeignKey(related_name='tokens', to='corpus.Line')),
                ('script', models.ForeignKey(related_name='tokens', to='corpus.Script')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='token',
            index_together=set([('script', 'type')]),
        ),
        migrations.AlterIndexTogether(
            name='script',
            index_together=set([('dataset', 'last_modified'), ('dataset', 'name')]),
        ),
        migrations.AddField(
            model_name='line',
            name='script',
            field=models.ForeignKey(related_name='lines', to='corpus.Script'),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='line',
            index_together=set([('script', 'number')]),
        ),
    ]
