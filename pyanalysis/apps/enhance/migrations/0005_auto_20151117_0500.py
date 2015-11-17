# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0004_auto_20151117_0459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dicttoken',
            name='text',
            field=models.TextField(default=b'', null=True, blank=True),
            preserve_default=True,
        ),
    ]
