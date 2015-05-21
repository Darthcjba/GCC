# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adjunto',
            name='lenguaje',
            field=models.CharField(max_length=10, null=True, choices=[(b'clike', b'C'), (b'python', b'Python'), (b'ruby', b'Ruby'), (b'css', b'CSS'), (b'php', b'PHP'), (b'scala', b'Scala'), (b'sql', b'SQL'), (b'bash', b'Bash'), (b'javascript', b'JavaScript'), (b'markup', b'Markup')]),
        ),
        migrations.AlterField(
            model_name='nota',
            name='fecha',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
