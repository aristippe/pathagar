# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import books.models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0015_auto_20160229_0000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover_img',
            field=books.models.ImageField(upload_to=b'covers', null=True, verbose_name='cover', blank=True),
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
