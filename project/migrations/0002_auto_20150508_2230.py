# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sprint',
            name='proyecto',
            field=models.ForeignKey(to='project.Proyecto', blank=True),
        ),
    ]
