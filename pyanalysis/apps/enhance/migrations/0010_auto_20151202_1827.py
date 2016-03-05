# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0009_auto_20151130_2054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='name',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='topicmodel',
            name='name',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
    ]
