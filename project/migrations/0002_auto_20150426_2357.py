# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstory',
            name='prioridad',
            field=models.IntegerField(default=0, choices=[(0, b'Baja'), (1, b'Media'), (2, b'Alta')]),
        ),
    ]
