# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_auto_20150324_2209'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='flujo',
            options={'verbose_name_plural': 'flujos', 'permissions': (('add_flow_template', 'add flow template'), ('change_flow_template', 'change flow template'), ('delete_flow_template', 'delete flow template'))},
        ),
        migrations.AlterModelOptions(
            name='proyecto',
            options={'permissions': (('list_all_projects', 'list all available projects'),)},
        ),
    ]
