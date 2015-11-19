# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0005_auto_20151117_0500'),
    ]

    operations = [
        migrations.AddField(
            model_name='similaritypair',
            name='type',
            field=models.CharField(default=b'cosine', max_length=32, db_index=True),
            preserve_default=True,
        ),
    ]
