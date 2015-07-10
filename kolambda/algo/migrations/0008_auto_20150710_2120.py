# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0007_algorithm_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='algorithm',
            name='judge_problem',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='algorithm',
            name='judge_space',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
