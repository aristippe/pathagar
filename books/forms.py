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

from django import forms
from django.utils.translation import ugettext as _

from dal import autocomplete
from django import forms

import models
from epub import Epub


class AuthorCreateMultipleField(autocomplete.CreateModelMultipleField):
    def create_value(self, value):
        return models.Author.objects.create(name=value).pk


class BookCreateField(autocomplete.CreateModelField):
    def create_value(self, value):
        return models.Book.objects.create(name=value).pk


class BookCreateMultipleField(autocomplete.CreateModelMultipleField):
    def create_value(self, value):
        return models.Book.objects.create(name=value).pk


class PublisherCreateMultipleField(autocomplete.CreateModelMultipleField):
    def create_value(self, value):
        return models.Publisher.objects.create(name=value).pk


class AdminAuthorsForm(forms.ModelForm):
    books = BookCreateField(
        required=False,
        queryset=models.Book.objects.all(),
        widget=autocomplete.ModelSelect2(url='book_autocomplete'),
    )

    class Meta:
        model = models.Author
        fields = ('name', 'books')


class AdminBooksForm(forms.ModelForm):
    authors = AuthorCreateMultipleField(
        required=False,
        queryset=models.Author.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='author_autocomplete'),
    )

    class Meta:
        model = models.Book
        exclude = ['mimetype']


class AuthorEditForm(forms.ModelForm):
    books = BookCreateMultipleField(
        required=False,
        queryset=models.Book.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='book_autocomplete'),
    )

    class Meta:
        model = models.Author
        fields = ('name', 'description', 'website', 'headshot', 'books')


class BookAddTagsForm(forms.Form):
    tags = forms.CharField()

    class Meta:
        model = models.Book
        fields = ['tags']


class BookEditForm(forms.ModelForm):
    authors = AuthorCreateMultipleField(
        label=_('Author(s)'),
        required=False,
        queryset=models.Author.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='author_autocomplete'),
    )
    publishers = PublisherCreateMultipleField(
        label=_('Publisher(s)'),
        required=False,
        queryset=models.Publisher.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='publisher_autocomplete'),
    )

    # tags = autocomplete.TaggitField(
    #     required=False,
    #     widget=autocomplete.TagSelect2(url='tags_autocomplete'),
    # )

    class Meta:
        model = models.Book
        fields = ['title', 'authors', 'publishers', 'dc_language', 'dc_issued',
                  'a_status', 'tags', 'downloads', 'summary', 'cover_img']

        # TODO: move some of these to models directly?
        labels = {'dc_language': _('Language'),
                  'dc_issued': _('Published'),
                  'a_status': _('Status'),
                  }


class BookUploadForm(forms.Form):
    epub_file = forms.FileField()

    def clean_epub_file(self):
        """Perform basic validation of the epub_file by making sure:
        - no other existing models have the same sha256 hash.
        - it is parseable by `Epub`.

        TODO: This method is called twice during the wizard (at step 0, and
        at done()), by Django design. Still, we should look for alternatives
        in order to make sure epub validation only happens once.
        https://code.djangoproject.com/ticket/10810
        """
        data = self.cleaned_data['epub_file']

        # Validate sha256 hash.
        sha256sum = models.sha256_sum(data)
        if models.Book.objects.filter(file_sha256sum=sha256sum).exists():
            raise forms.ValidationError('The file is already on the database')

        # Validate parseability.
        epub = None
        try:
            # Fetch information from the epub, and set it as attributes.
            epub = Epub(data)
            info_dict, cover_path, tags = epub.as_model_dict()

            # TODO: pass this info via a cleaner way.
            self.cleaned_data['original_path'] = data.name
            self.cleaned_data['info_dict'] = info_dict
            self.cleaned_data['cover_path'] = cover_path
            self.cleaned_data['file_sha256sum'] = sha256sum
        except Exception as e:
            raise forms.ValidationError(str(e))
        finally:
            # Try to remove the temp extracted epub folder.
            try:
                epub.close()
            except:
                pass

        return data


class BookMetadataForm(BookEditForm):
    class Meta:
        model = models.Book
        exclude = ('book_file',
                   'original_path', 'mimetype', 'file_sha256sum', 'cover_img')

        # TODO: move some of these to models directly?
        labels = {'dc_language': _('Language'),
                  'dc_issued': _('Published'),
                  'a_status': _('Status'),
                  }


class AddLanguageForm(forms.ModelForm):
    class Meta:
        model = models.Language
        exclude = ('code',)
