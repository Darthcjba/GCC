# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0007_auto_20150408_0204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proyecto',
            name='duracion_sprint',
            field=models.PositiveIntegerField(default=30),
            preserve_default=True,
        ),
    ]
