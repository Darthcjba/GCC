# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_auto_20150324_1442'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='miembroequipo',
            options={'verbose_name_plural': 'miembros equipo'},
        ),
        migrations.AlterModelOptions(
            name='userstory',
            options={'verbose_name_plural': 'user stories'},
        ),
    ]
