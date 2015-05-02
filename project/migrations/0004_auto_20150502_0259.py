# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_auto_20150502_0053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commit',
            name='actividad',
        ),
        migrations.RemoveField(
            model_name='commit',
            name='revision',
        ),
        migrations.RemoveField(
            model_name='commit',
            name='sprint',
        ),
        migrations.DeleteModel(
            name='Commit',
        ),
    ]
