# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_adjunto_lenguaje'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adjunto',
            name='lenguaje',
            field=models.CharField(default=b'css', max_length=10, choices=[(b'clike', b'C'), (b'python', b'Python'), (b'ruby', b'Ruby'), (b'css', b'CSS'), (b'php', b'PHP'), (b'scala', b'Scala'), (b'sql', b'SQL'), (b'bash', b'Bash'), (b'javascript', b'JavaScript')]),
        ),
    ]
