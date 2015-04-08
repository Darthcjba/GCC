# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_sprint_nombre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sprint',
            name='nombre',
            field=models.CharField(default=b'', max_length=20, blank=True),
            preserve_default=True,
        ),
    ]
