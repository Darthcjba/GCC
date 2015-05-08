# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0007_auto_20150507_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='adjunto',
            name='binary',
            field=models.BinaryField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
