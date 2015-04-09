# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0006_auto_20150407_2323'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='miembroequipo',
            name='rol',
        ),
        migrations.AddField(
            model_name='miembroequipo',
            name='roles',
            field=models.ManyToManyField(to='auth.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proyecto',
            name='equipo',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='project.MiembroEquipo'),
            preserve_default=True,
        ),
    ]
