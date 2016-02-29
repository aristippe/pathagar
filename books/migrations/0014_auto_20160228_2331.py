# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0013_auto_20160228_1800'),
    ]

    operations = [
        migrations.RenameField('Book', 'a_title', 'title'),
    ]
