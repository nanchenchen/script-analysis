# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0016_scriptdiff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scriptdiff',
            name='pair',
            field=models.ForeignKey(related_name='diff', to='enhance.SimilarityPair', unique=True),
            preserve_default=True,
        ),
    ]
