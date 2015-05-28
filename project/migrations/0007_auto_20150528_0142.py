# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_auto_20150528_0139'),
    ]

    operations = [
        migrations.RenameField(
            model_name='nota',
            old_name='horas_registradas',
            new_name='horas_a_registrar',
        ),
    ]
