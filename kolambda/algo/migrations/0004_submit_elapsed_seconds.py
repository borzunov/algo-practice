# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0003_auto_20150521_0342'),
    ]

    operations = [
        migrations.AddField(
            model_name='submit',
            name='elapsed_seconds',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
    ]
