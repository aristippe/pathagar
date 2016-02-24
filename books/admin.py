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

from django.contrib import admin
import models as books_models


class BookAdmin(admin.ModelAdmin):
    fieldsets = [
        ('File information', {
            'fields': ['book_file', 'original_path', 'file_sha256sum',
                       'mimetype', 'cover_img']}),
        ('Basic information',
         {'fields': ['a_title', 'authors', 'a_status', 'tags']}),
        ('Extended information', {
            'fields': ['a_summary', 'a_category', 'a_rights', 'a_id',
                       'dc_language', 'dc_publisher', 'dc_issued',
                       'dc_identifier', 'time_added', 'a_updated',
                       'downloads'],
            'classes': ['collapse']}),
    ]

    def authors(self, user):
        authors = []
        for author in user.author.all():
            authors.append(author.name)
        return ', '.join(authors)

    authors.short_description = 'Authors'

    list_display = ('a_title', 'authors', 'time_added', 'original_path')

    readonly_fields = ('time_added', 'a_updated', 'a_id')


class TagGroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(books_models.Book, BookAdmin)
admin.site.register(books_models.Language)
admin.site.register(books_models.Status)
admin.site.register(books_models.TagGroup, TagGroupAdmin)
