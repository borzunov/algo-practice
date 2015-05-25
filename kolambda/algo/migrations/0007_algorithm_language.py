# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from ..models import Language


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0006_auto_20150525_0931'),
    ]

    operations = [
        migrations.AddField(
            model_name='algorithm',
            name='language',
            field=models.ForeignKey(to='algo.Language', default=1),
            preserve_default=False,
        ),
    ]
