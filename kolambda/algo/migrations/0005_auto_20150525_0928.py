# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0004_submit_elapsed_seconds'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('editor_mode', models.SlugField(max_length=60)),
            ],
        ),
        migrations.AlterField(
            model_name='algorithm',
            name='slug',
            field=models.SlugField(max_length=60),
        ),
    ]
