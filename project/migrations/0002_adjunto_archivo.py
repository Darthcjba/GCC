# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='adjunto',
            name='archivo',
            field=models.FileField(null=True, upload_to=b'user_story'),
            preserve_default=True,
        ),
    ]
