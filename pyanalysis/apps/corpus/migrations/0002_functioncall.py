# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FunctionCall',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=255, null=True, db_index=True, blank=True)),
                ('script', models.ForeignKey(related_name='calls', to='corpus.Script')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
