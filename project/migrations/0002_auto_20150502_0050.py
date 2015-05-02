# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='nota',
            old_name='descripcion',
            new_name='mensaje',
        ),
        migrations.AddField(
            model_name='nota',
            name='horas_registradas',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
