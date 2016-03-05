# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0002_functioncall'),
        ('enhance', '0010_auto_20151202_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='tokenvectorelement',
            name='line',
            field=models.ForeignKey(related_name='token_vector_elements', default=None, blank=True, to='corpus.Line', null=True),
            preserve_default=True,
        ),
    ]
