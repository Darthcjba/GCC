# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_auto_20150502_0050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nota',
            name='mensaje',
            field=models.TextField(help_text=b'Mensaje de descripcion de los avances'),
        ),
    ]
