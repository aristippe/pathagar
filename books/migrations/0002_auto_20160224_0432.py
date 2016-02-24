# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ('-time_added',), 'get_latest_by': 'time_added', 'verbose_name': 'book', 'verbose_name_plural': 'books'},
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
            field=models.ImageField(upload_to=b'covers', null=True, verbose_name='cover', blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='time_added',
            field=models.DateTimeField(auto_now_add=True, verbose_name='time added'),
        ),
    ]
