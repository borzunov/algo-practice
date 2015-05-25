# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0005_auto_20150525_0928'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='language',
            name='editor_mode',
        ),
        migrations.AddField(
            model_name='language',
            name='mime_type',
            field=models.CharField(max_length=60, default='text/x-c++src'),
            preserve_default=False,
        ),
    ]
