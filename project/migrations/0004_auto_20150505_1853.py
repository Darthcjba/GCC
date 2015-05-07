# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_adjunto_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adjunto',
            name='type',
        ),
        migrations.AddField(
            model_name='adjunto',
            name='tipo',
            field=models.CharField(default=b'text', max_length=10, choices=[(b'Imagen', b'img'), (b'Texto', b'text'), (b'Multimedia', b'mmedia'), (b'Binario', b'bin')]),
            preserve_default=True,
        ),
    ]
