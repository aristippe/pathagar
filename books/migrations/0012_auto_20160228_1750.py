# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0011_auto_20160226_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='description',
            field=models.TextField(null=True, verbose_name='desription', blank=True),
        ),
        migrations.AddField(
            model_name='author',
            name='headshot',
            field=models.ImageField(upload_to=b'author_headshots', null=True, verbose_name='headshot', blank=True),
        ),
        migrations.AddField(
            model_name='author',
            name='website',
            field=models.URLField(null=True, verbose_name='website', blank=True),
        ),
    ]
