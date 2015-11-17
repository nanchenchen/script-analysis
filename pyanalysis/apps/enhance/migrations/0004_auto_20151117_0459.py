# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0003_auto_20151117_0456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dicttoken',
            name='text',
            field=models.CharField(max_length=256),
            preserve_default=True,
        ),
    ]
