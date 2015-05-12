# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0009_auto_20150508_1817'),
    ]

    operations = [
        migrations.AddField(
            model_name='adjunto',
            name='content_type',
            field=models.CharField(max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
    ]
