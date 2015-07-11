# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0012_submit_judge_test'),
    ]

    operations = [
        migrations.AddField(
            model_name='submit',
            name='awaiting_for_verdict',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
