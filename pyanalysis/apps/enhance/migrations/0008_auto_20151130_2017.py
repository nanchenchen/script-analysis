# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0007_auto_20151130_2013'),
    ]

    operations = [
        migrations.AddField(
            model_name='dictionary',
            name='name',
            field=models.CharField(default=b'', max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dictionary',
            name='settings',
            field=models.TextField(default=b'', null=True, blank=True),
            preserve_default=True,
        ),
    ]
