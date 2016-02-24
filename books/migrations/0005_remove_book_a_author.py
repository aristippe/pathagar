# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_auto_20160224_0504'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='a_author',
        ),
    ]
