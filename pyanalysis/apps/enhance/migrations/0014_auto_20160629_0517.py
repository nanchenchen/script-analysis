# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0013_differencenote_relative_relations'),
    ]

    operations = [
        migrations.RenameField(
            model_name='differencenote',
            old_name='relative_relations',
            new_name='relative_relation',
        ),
    ]
