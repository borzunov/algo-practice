# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0010_auto_20150710_2220'),
    ]

    operations = [
        migrations.AddField(
            model_name='submit',
            name='judge_verdict',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
