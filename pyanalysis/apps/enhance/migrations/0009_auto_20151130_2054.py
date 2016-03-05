# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0008_auto_20151130_2017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicmodel',
            name='name',
            field=models.TextField(default=b'', blank=b''),
            preserve_default=True,
        ),
    ]
