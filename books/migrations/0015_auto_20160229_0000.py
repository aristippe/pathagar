# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0014_auto_20160228_2331'),
    ]

    operations = [
        migrations.RenameField('Book', 'a_summary', 'summary'),
    ]
