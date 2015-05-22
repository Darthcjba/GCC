# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_auto_20150521_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='nota',
            name='estado',
            field=models.IntegerField(default=0, choices=[(0, b'Inactivo'), (1, b'En curso'), (2, b'Pendiente Aprobacion'), (3, b'Aprobado')]),
            preserve_default=True,
        ),
    ]
