# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0009_language_judge_language'),
    ]

    operations = [
        migrations.RenameField(
            model_name='algorithm',
            old_name='judge_problem',
            new_name='judge_problem_id',
        ),
        migrations.RenameField(
            model_name='algorithm',
            old_name='judge_space',
            new_name='judge_space_id',
        ),
        migrations.RenameField(
            model_name='language',
            old_name='judge_language',
            new_name='judge_language_id',
        ),
    ]
