# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0008_auto_20150710_2120'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='judge_language',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
    ]
