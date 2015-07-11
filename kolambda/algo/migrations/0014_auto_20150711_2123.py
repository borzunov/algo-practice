# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0013_submit_awaiting_for_verdict'),
    ]

    operations = [
        migrations.AddField(
            model_name='submit',
            name='judge_comment',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submit',
            name='judge_submit_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
