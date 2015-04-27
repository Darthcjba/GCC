# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_auto_20150426_2357'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='version',
            name='user_story',
        ),
        migrations.DeleteModel(
            name='Version',
        ),
    ]
