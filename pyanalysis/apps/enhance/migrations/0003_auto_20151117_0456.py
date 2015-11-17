# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0002_similaritypair'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dicttoken',
            name='text',
            field=models.CharField(max_length=1024),
            preserve_default=True,
        ),
    ]
