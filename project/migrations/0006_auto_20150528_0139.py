# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_nota_horas_a_registrar'),
    ]

    operations = [
        migrations.RenameField(
            model_name='nota',
            old_name='horas_a_registrar',
            new_name='tiempo_registrado',
        ),
    ]
