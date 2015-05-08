# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0008_adjunto_binary'),
    ]

    operations = [
        migrations.RenameField(
            model_name='adjunto',
            old_name='binary',
            new_name='binario',
        ),
    ]
