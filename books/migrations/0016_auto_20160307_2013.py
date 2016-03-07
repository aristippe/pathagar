# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0015_auto_20160229_0000'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TagGroup',
        ),
        migrations.AlterField(
            model_name='book',
            name='summary',
            field=models.TextField(null=True, verbose_name='summary', blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(max_length=255, verbose_name='title'),
        ),
    ]
