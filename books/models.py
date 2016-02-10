# Copyright (C) 2010, One Laptop Per Child
# Copyright (C) 2010, Kushal Das
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from hashlib import sha256

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager  # NEW

from langlist import langs_by_code
from storage import LinkOrFileSystemStorage
from uuidfield import UUIDField


def sha256_sum(_file):  # used to generate sha256 sum of book files
    s = sha256()
    for chunk in _file:
        s.update(chunk)
    return s.hexdigest()


class LanguageManager(models.Manager):
    def get_or_create_by_code(self, code):
        """Convenience method for returning the Language that corresponds to
        the specified code, creating it if needed.
        If the code is not valid, it raises a ValueError.

        TODO: replace with a RFC5646 compatible system.
        TODO: find the proper Exception to subclass.
        TODO: revise fixtures, some (or all) of them might be unreachable.
        """
        # Add Language, discarding it if it does not have a valid code.
        if code in langs_by_code:
            language, _ = self.get_or_create(
                code=code, label=langs_by_code[code])
            return language
        raise ValueError('%s is not a valid language code' % code)  # TODO lang


class Language(models.Model):
    # Custom manager for using get_or_create_by_code().
    objects = LanguageManager()

    label = models.CharField(_('language name'), max_length=50, blank=True,
                             unique=False)
    code = models.CharField(max_length=5, blank=True, unique=True)

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")

    def __unicode__(self):
        return self.label


class TagGroup(models.Model):
    name = models.CharField(max_length=200, blank=False)
    slug = models.SlugField(max_length=200, blank=False)

    # tags = TagableManager()

    class Meta:
        verbose_name = _("Tag group")
        verbose_name_plural = _("Tag groups")

    def __unicode__(self):
        return self.name


class Status(models.Model):
    status = models.CharField(max_length=200, blank=False)

    class Meta:
        verbose_name = _("Status")
        verbose_name_plural = _("Status")

    def __unicode__(self):
        return self.status


class Book(models.Model):
    """
    This model stores the book file, and all the metadata that is
    needed to publish it in a OPDS atom feed.

    It also stores other information, like tags and downloads, so the
    book can be listed in OPDS catalogs.

    """

    # https://stackoverflow.com/questions/8332443/set-djangos-filefield-to-an-existing-file
    # https://stackoverflow.com/questions/10905674/django-how-to-save-original-filename-in-filefield
    # get model instance you want to set the value on...set the value..save it

    # File related fields.
    book_file = models.FileField(upload_to='books', null=False,
                                 storage=LinkOrFileSystemStorage())
    # TODO: OS X 10.10 1016 chars? remove max_length entirely?
    original_path = models.CharField(_('file'), max_length=1016)
    file_sha256sum = models.CharField(max_length=64, unique=True)
    mimetype = models.CharField(max_length=200, null=True)
    cover_img = models.ImageField(_('cover'), upload_to='covers',
                                  blank=True, null=True)

    # Atom fields.
    a_id = UUIDField('atom:id')
    a_title = models.CharField(_('atom:title'), max_length=200, null=False)
    a_author = models.CharField(_('atom:author'), max_length=200)
    a_updated = models.DateTimeField(_('atom:updated'), auto_now=True)
    a_summary = models.TextField(_('atom:summary'), blank=True, null=True)
    a_category = models.CharField(_('atom:category'),
                                  max_length=200, blank=True, null=True)
    a_rights = models.CharField(_('atom:rights'),
                                max_length=200, blank=True, null=True)

    # Info fields.
    dc_language = models.ForeignKey(Language, blank=True, null=True)
    dc_publisher = models.CharField(_('dc:publisher'),
                                    max_length=200, blank=True, null=True)
    dc_issued = models.CharField(_('dc:issued'),
                                 max_length=100, blank=True, null=True)
    dc_identifier = models.CharField(_('dc:identifier'),
                                     max_length=50, blank=True, null=True,
                                     help_text=_('Use ISBN for this'))

    # Other fields.
    a_status = models.ForeignKey(Status, blank=False, null=True)
    time_added = models.DateTimeField(_('time added'), auto_now_add=True)
    tags = TaggableManager(blank=True)
    downloads = models.IntegerField(default=0)

    class Meta:
        verbose_name = _('book')
        verbose_name_plural = _('books')
        ordering = ('-time_added',)
        get_latest_by = "time_added"

    def __unicode__(self):
        return self.a_title

    @models.permalink
    def get_absolute_url(self):
        return 'pathagar.books.views.book_detail', [self.pk]


@receiver(post_delete, sender=Book)
def book_post_delete_handler(**kwargs):
    """
    Book model post_delete handler to ensure book and cover files are removed
    with book. Check if optional cover exists to avoid error.
    """
    book = kwargs['instance']

    book.book_file.delete(save=False)

    if book.cover_img:
        book.cover_img.delete(save=False)
