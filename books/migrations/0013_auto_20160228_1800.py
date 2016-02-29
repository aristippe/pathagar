# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0012_auto_20160228_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='description',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
    ]
