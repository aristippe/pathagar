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
from django.db.models import Count
import models as books_models
from forms import AdminAuthorsForm, AdminBooksForm
from django.utils.translation import ugettext_lazy as _


class AuthorsInline(admin.TabularInline):
    model = books_models.Book.authors.through


class PublishersInline(admin.TabularInline):
    model = books_models.Book.publishers.through


class AuthorAdmin(admin.ModelAdmin):
    form = AdminAuthorsForm

    inlines = [
        AuthorsInline,
    ]

    search_fields = ['name']

    list_display = ('name', 'book_count')

    def get_queryset(self, request):
        return books_models.Author.objects.annotate(book_count=Count('books'))

    def book_count(self, inst):
        return inst.book_count

    book_count.admin_order_field = 'book_count'


class BookAdmin(admin.ModelAdmin):
    form = AdminBooksForm

    fieldsets = [
        ('File information', {
            'fields': ['book_file', 'original_path',
                       'cover_img']}),
        ('Basic information',
         {'fields': ['title', 'a_status', 'tags']}),
        ('Extended information', {
            'fields': ['summary', 'a_category', 'a_rights', 'a_id',
                       'dc_language', 'dc_issued',
                       'dc_identifier', 'time_added', 'a_updated',
                       'downloads', 'uploader'],
            'classes': ['collapse']}),
    ]

    inlines = [
        AuthorsInline, PublishersInline
    ]

    list_display = ('title', 'get_authors', 'time_added')
    readonly_fields = ('time_added', 'a_updated', 'a_id')
    search_fields = ['title', 'authors__name', 'publishers__name']


class PublisherAdmin(admin.ModelAdmin):
    inlines = [
        PublishersInline,
    ]

    list_display = ('name', 'book_count')
    search_fields = ['name']

    def get_queryset(self, request):
        return books_models.Publisher.objects.annotate(book_count=Count(
            'books'))

    def book_count(self, inst):
        return inst.book_count

    book_count.admin_order_field = 'book_count'


admin.site.register(books_models.Author, AuthorAdmin)
admin.site.register(books_models.Book, BookAdmin)
admin.site.register(books_models.Language)
admin.site.register(books_models.Publisher, PublisherAdmin)
admin.site.register(books_models.Status)
