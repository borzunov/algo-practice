# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='submit',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 19, 4, 12, 46, 137149)),
            preserve_default=False,
        ),
    ]
