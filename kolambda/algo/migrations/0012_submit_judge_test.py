# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0011_submit_judge_verdict'),
    ]

    operations = [
        migrations.AddField(
            model_name='submit',
            name='judge_test',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
