# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-11 07:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_auto_20160211_0707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='a_author',
            field=models.CharField(max_length=200, verbose_name=b'atom:author'),
        ),
        migrations.DeleteModel(
            name='Author',
        ),
    ]
