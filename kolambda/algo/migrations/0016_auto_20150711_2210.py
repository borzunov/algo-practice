# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0015_auto_20150711_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submit',
            name='judge_comment',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
