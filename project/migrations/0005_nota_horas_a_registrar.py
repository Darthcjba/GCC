# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_auto_20150527_0143'),
    ]

    operations = [
        migrations.AddField(
            model_name='nota',
            name='horas_a_registrar',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
