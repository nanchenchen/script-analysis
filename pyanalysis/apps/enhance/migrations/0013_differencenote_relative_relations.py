# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0012_auto_20160615_2248'),
    ]

    operations = [
        migrations.AddField(
            model_name='differencenote',
            name='relative_relations',
            field=models.CharField(default=b'U', max_length=1, choices=[(b'-1', b'src is older'), (b'0', b'may be the same'), (b'1', b'tar is older'), (b'U', b'Undefined')]),
            preserve_default=True,
        ),
    ]
