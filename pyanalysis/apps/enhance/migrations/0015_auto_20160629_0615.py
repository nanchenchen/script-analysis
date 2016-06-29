# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0014_auto_20160629_0517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='differencenote',
            name='relative_relation',
            field=models.CharField(default=b'U', max_length=1, choices=[(b'<', b'src is older'), (b'=', b'may be the same'), (b'>', b'tar is older'), (b'?', b'tar is older'), (b'U', b'Undefined')]),
            preserve_default=True,
        ),
    ]
