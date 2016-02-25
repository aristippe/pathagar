# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def make_many_authors(apps, schema_editor):
    """
        Adds the Author object in Book.a_author to the
        many-to-many relationship in Book.authors
    """

    Author = apps.get_model('books', 'Author')
    Book = apps.get_model('books', 'Book')

    for book in Book.objects.all():
        try:
            author = Author.objects.get(name=book.a_author)
        except Author.DoesNotExist:
            author = Author(name=book.a_author)
            author.save()
        book.authors.add(author)


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_auto_20160224_0504'),
    ]

    operations = [
        migrations.RunPython(make_many_authors),
    ]
