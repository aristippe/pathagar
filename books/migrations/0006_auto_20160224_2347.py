# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_remove_book_a_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='a_rights',
            field=models.CharField(max_length=255, null=True, verbose_name='atom:rights', blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='a_title',
            field=models.CharField(max_length=255, verbose_name='atom:title'),
        ),
        migrations.AlterField(
            model_name='book',
            name='dc_identifier',
            field=models.CharField(help_text='Use ISBN for this', max_length=100, null=True, verbose_name='dc:identifier', blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='dc_publisher',
            field=models.CharField(max_length=255, null=True, verbose_name='dc:publisher', blank=True),
        ),
    ]
