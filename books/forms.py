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

import models
from epub import Epub


class BookUploadForm(forms.Form):
    epub_file = forms.FileField()

    def clean_epub_file(self):
        """Perform basic validation of the epub_file by making sure:
        - no other existing models have the same sha256 hash.
        - it is  parseable by `Epub`.

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
        try:
            # Fetch information from the epub, and set it as attributes.
            epub = Epub(data)
            info_dict, cover_path = epub.as_model_dict()

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


class BookMetadataForm(forms.ModelForm):
    class Meta:
        model = models.Book
        exclude = ('book_file', 'original_path', 'mimetype',
                   'file_sha256sum', 'cover_img')


class BookForm(forms.ModelForm):
    # dc_language = ModelChoiceField(Language.objects, widget=SelectWithPop)

    class Meta:
        model = models.Book
        exclude = ('original_path', 'mimetype', 'file_sha256sum',)

    def save(self, commit=True):
        """
        Store the MIME type of the uploaded book in the database.

        This is given by the browser in the POST request.

        """
        instance = super(BookForm, self).save(commit=False)
        book_file = self.cleaned_data['book_file']
        if instance.mimetype is None:
            try:
                instance.mimetype = book_file.content_type
            except:
                pass
        if commit:
            instance.save()
        return instance


class AddLanguageForm(forms.ModelForm):
    class Meta:
        model = models.Language
        exclude = ('code',)
