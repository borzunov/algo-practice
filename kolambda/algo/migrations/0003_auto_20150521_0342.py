# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0002_submit_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='algorithm',
            name='slug',
            field=models.SlugField(blank=True, max_length=60),
        ),
        migrations.AlterField(
            model_name='submit',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
