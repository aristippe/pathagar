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

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager

from langlist import langs_by_code
from storage import LinkOrFileSystemStorage
from uuidfield import UUIDField
from books.utils import standardize_language


def sha256_sum(_file):  # used to generate sha256 sum of book files
    s = sha256()
    for chunk in _file:
        s.update(chunk)
    return s.hexdigest()


class ImageField(models.ImageField):
    """Custom ImageField that automatically deletes the old image when it is
    modified via a ModelForm (either by clicking on the "clear" checkbox, or
    selecting a new image with the "upload" button).
    """
    def save_form_data(self, instance, data):
        if data is not None:
            file_ = getattr(instance, self.attname)
            if file_ != data:
                file_.delete(save=False)
        super(ImageField, self).save_form_data(instance, data)


@python_2_unicode_compatible
class Author(models.Model):
    name = models.CharField(_('author'), unique=True, max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    headshot = models.ImageField(_('headshot'), upload_to='author_headshots',
                                 blank=True, null=True)
    website = models.URLField(_('website'), blank=True, null=True)

    # __unicode__ on Python 2
    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class LanguageManager(models.Manager):
    def get_or_create_by_code(self, code):
        """Convenience method for returning the Language that corresponds to
        the specified code, creating it if needed.
        If the code is not valid, it raises a ValueError.

        :param code: language code
        :returns: language
        """
        # Try to fetch the Language if already on DB.
        try:
            language = self.get(code=code)
            return language
        except Language.DoesNotExist:
            pass

        # Add Language, discarding it if it does not have a valid code.
        std = standardize_language(code)
        if std:
            long_name = "%s%s" % (std.description[0],
                                  ' (%s)' % ', '.join(std.description[1:]) if
                                  len(std.description) > 1 else '')
            language = self.create(code=std.code,
                                   label=std.description[0],
                                   long_name=long_name)
            return language

        raise ValueError('%s is not a valid language code' % code)


class Language(models.Model):
    """Model for a RFC5646 language.
    * `code` is a lowercase RFC5646 tag (ie. "en-gb")
    * `label` is the first element name (ie. "English")
    * `long_name` is the full description, including the first element name and
    subsequents elements (if any) between parenthesis and separated by commas
    (ie. "English (United Kingdom)")
    """
    # Custom manager for using get_or_create_by_code().
    objects = LanguageManager()

    # max_length is set following recommendations of RFC5646 section 4.1.
    code = models.CharField(max_length=50, unique=True)
    label = models.CharField(_('language name'), max_length=128)
    long_name = models.CharField(max_length=1024)

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")
        ordering = ('long_name',)

    def __unicode__(self):
        return self.long_name


@python_2_unicode_compatible
class Publisher(models.Model):
    name = models.CharField(_('publisher'), unique=True, max_length=255)

    # __unicode__ on Python 2
    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


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

    # File related fields.
    book_file = models.FileField(upload_to='books', null=False,
                                 storage=LinkOrFileSystemStorage())
    # TODO: OS X 10.10 1016 chars? remove max_length entirely?
    original_path = models.CharField(_('file'), max_length=1016)
    file_sha256sum = models.CharField(max_length=64, unique=True)
    mimetype = models.CharField(max_length=200, null=True)
    cover_img = ImageField(_('cover'), upload_to='covers',
                           blank=True, null=True)

    # General fields
    title = models.CharField(_('title'), max_length=255, null=False)
    authors = models.ManyToManyField(Author, blank=True, related_name='books')
    publishers = models.ManyToManyField(Publisher, blank=True,
                                        related_name='books')
    dc_language = models.ForeignKey(Language, blank=True, null=True)
    summary = models.TextField(_('summary'), blank=True, null=True)

    # ePub atom fields
    a_id = UUIDField('atom:id')
    a_updated = models.DateTimeField(_('atom:updated'), auto_now=True)
    a_category = models.CharField(_('atom:category'),
                                  max_length=200, blank=True, null=True)
    a_rights = models.TextField(_('atom:rights'), blank=True, null=True)

    # ePub info fields.
    dc_issued = models.CharField(_('dc:issued'),
                                 max_length=100, blank=True, null=True)
    dc_identifier = models.CharField(_('dc:identifier'),
                                     max_length=100, blank=True, null=True,
                                     help_text=_('Use ISBN for this'))

    # Other fields.
    uploader = models.ForeignKey(User, blank=True, null=True, default=None)
    # TODO a_status null=True?
    a_status = models.ForeignKey(Status, blank=False, null=False)
    time_added = models.DateTimeField(_('time added'), auto_now_add=True)
    tags = TaggableManager(blank=True,
                           help_text=_("A comma-separated list of tags."))
    downloads = models.IntegerField(default=0)

    class Meta:
        verbose_name = _('book')
        verbose_name_plural = _('books')
        ordering = ('-time_added',)
        get_latest_by = "time_added"

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return 'book_detail', [self.pk]

    def get_authors(self):
        return ", ".join([str(p) for p in self.authors.all()])

    # def save(self, *args, **kwargs):
    #     import urllib2
    #     from django.core.files import File
    #     from django.core.files.temp import NamedTemporaryFile
    #
    #     if self.cover_img_url:
    #         img_temp = NamedTemporaryFile(delete=True)
    #         img_temp.write(urllib2.urlopen(self.cover_img_url).read())
    #         img_temp.flush()
    #         self.cover_img.file.save(img_filename, File(img_temp))
    #         self.cover_img_url = ''
    #         super(Book, self).save()


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
