# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0014_auto_20150711_2123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submit',
            name='judge_comment',
            field=models.TextField(null=True, blank=True),
        ),
    ]
