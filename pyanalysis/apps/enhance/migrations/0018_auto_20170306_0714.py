# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0017_auto_20170306_0630'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scriptdiff',
            old_name='content',
            new_name='text',
        ),
    ]
