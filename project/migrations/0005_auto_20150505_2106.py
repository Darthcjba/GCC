# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_auto_20150505_1853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adjunto',
            name='tipo',
            field=models.CharField(default=b'text', max_length=10, choices=[(b'img', b'Imagen'), (b'text', b'Texto'), (b'mmed', b'Multimedia'), (b'bin', b'Binario')]),
        ),
    ]
