# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0010_auto_20160225_2224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='a_rights',
            field=models.TextField(null=True, verbose_name='atom:rights', blank=True),
        ),
    ]
