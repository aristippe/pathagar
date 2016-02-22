# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-22 17:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_auto_20160211_0708'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'get_latest_by': 'time_added', 'ordering': ('-time_added',), 'verbose_name': 'book', 'verbose_name_plural': 'books'},
        ),
        migrations.AlterModelOptions(
            name='language',
            options={'verbose_name': 'Language', 'verbose_name_plural': 'Languages'},
        ),
        migrations.AlterModelOptions(
            name='status',
            options={'verbose_name': 'Status', 'verbose_name_plural': 'Status'},
        ),
        migrations.AlterField(
            model_name='book',
            name='cover_img',
            field=models.ImageField(blank=True, null=True, upload_to=b'covers', verbose_name='cover'),
        ),
        migrations.AlterField(
            model_name='book',
            name='time_added',
            field=models.DateTimeField(auto_now_add=True, verbose_name='time added'),
        ),
    ]
