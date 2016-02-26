# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0009_remove_book_dc_publisher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='authors',
            field=models.ManyToManyField(related_name='books', to='books.Author', blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='publishers',
            field=models.ManyToManyField(related_name='books', to='books.Publisher', blank=True),
        ),
    ]
