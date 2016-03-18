# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from books.utils import standardize_language


def standardize_existing(apps, schema_editor):
    """Custom cleanup of existing Languages:
    - change code to lowercase
    - set long_name and label based on standardize_language()
    """
    Language = apps.get_model('books', 'Language')
    for row in Language.objects.all():
        row.code = row.code.lower()
        std = standardize_language(row.code)
        if std:
            long_name = "%s%s" % (std.description[0],
                                  ' (%s)' % ', '.join(std.description[1:]) if
                                  len(std.description) > 1 else '')
            row.label = std.description[0]
            row.long_name = long_name
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0018_book_uploader'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='language',
            options={'ordering': ('long_name',), 'verbose_name': 'Language', 'verbose_name_plural': 'Languages'},
        ),
        migrations.AddField(
            model_name='language',
            name='long_name',
            field=models.CharField(default='xxx', max_length=1024),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='language',
            name='code',
            field=models.CharField(unique=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='language',
            name='label',
            field=models.CharField(max_length=128, verbose_name='language name'),
        ),
        migrations.RunPython(standardize_existing),
    ]
