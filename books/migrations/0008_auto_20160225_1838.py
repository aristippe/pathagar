# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def make_many_publishers(apps, schema_editor):
    """
        Adds the Publisher object in Book.a_publisher to the
        many-to-many relationship in Book.publishers
    """

    Publisher = apps.get_model('books', 'Publisher')
    Book = apps.get_model('books', 'Book')

    for book in Book.objects.all():
        if book.dc_publisher is not None:
            try:
                publisher = Publisher.objects.get(name=book.dc_publisher)
            except Publisher.DoesNotExist:
                publisher = Publisher(name=book.dc_publisher)
                publisher.save()
            book.publishers.add(publisher)


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_auto_20160225_1837'),
    ]

    operations = [
        migrations.RunPython(make_many_publishers),
    ]
