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

import logging
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.paginator import InvalidPage
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import FormView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import DeleteView, UpdateView
from django.views.generic.list import ListView

from dal import autocomplete
from formtools.wizard.views import SessionWizardView
from pure_pagination import Paginator, EmptyPage
from pure_pagination.mixins import PaginationMixin
from sendfile import sendfile
from taggit.models import Tag

from forms import (AuthorEditForm, BookAddTagsForm, BookEditForm,
                   AddLanguageForm)
from models import Author, Book, Language, Publisher, Status, TagGroup
from opds import (generate_catalog, generate_root_catalog,
                  generate_taggroups_catalog, generate_tags_catalog)
from opds import page_qstring
from popuphandler import handle_pop_add
from search import simple_search, advanced_search

logger = logging.getLogger(__name__)


class AuthorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Author.objects.none()

        qs = Author.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class BookAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Book.objects.none()

        qs = Book.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class PublisherAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Publisher.objects.none()

        qs = Publisher.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class TagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Tag.objects.none()

        qs = Tag.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class AddBookWizard(SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT,
                                                           'upload'))
    instance = None

    def get_form_instance(self, step):
        if self.instance is None:
            self.instance = Book()
        return self.instance

    def process_step_files(self, form):
        """Append the values appended by the first form to storage.extra_data.

        :param form:
        :returns:
        """
        if self.steps.current == '0':
            self.storage.extra_data = {
                'original_path': form.cleaned_data['original_path'],
                'info_dict': form.cleaned_data['info_dict'],
                'cover_path': form.cleaned_data['cover_path'],
                'file_sha256sum': form.cleaned_data['file_sha256sum']
            }

        return self.get_form_step_files(form)

    def get_form_initial(self, step):
        """Use the values parsed from the uploaded Epub as the initial values
        (on step 0) as the initial values for the form on step 1.

        :param step:
        :returns:
        """
        ret = super(AddBookWizard, self).get_form_initial(step)

        if step == '1':
            # Update the initial values with the epub information.
            info_dict = self.storage.extra_data['info_dict']
            ret.update(info_dict)
            ret['original_path'] = self.storage.extra_data['original_path']
            ret['a_status'] = Status.objects.get(
                status=settings.DEFAULT_BOOK_STATUS
            )

            try:
                # TODO: Language is created even if the Book is not saved.
                ret['dc_language'] = Language.objects.get_or_create_by_code(
                    info_dict['dc_language']
                )
            except ValueError:
                logger.warn('Invalid language: %s' %
                            str(info_dict['dc_language']))
                ret['dc_language'] = None
        return ret

    def done(self, form_list, **kwargs):
        """Create a new Book when all the forms have been submitted. The file
        uploaded on step 0 is added to the Book along with its sha256 hash, and
        the temporary cover filed (if applicable) is copied and deleted.

        :param form_list:
        :returns:
        """
        uploaded_file = form_list[0].cleaned_data['epub_file']
        # Set file related parameters.
        self.instance.book_file = uploaded_file
        self.instance.file_sha256sum = self.storage. \
            extra_data['file_sha256sum']
        self.instance.save()
        # Save the tags.
        self.instance.tags.add(*form_list[1].cleaned_data['tags'])

        # Set the cover image.
        tmp_cover_path = self.storage.extra_data['cover_path']
        cover_filename = None
        if tmp_cover_path:
            try:
                cover_filename = '%s%s' % (self.instance.pk,
                                           os.path.splitext(tmp_cover_path)[1])
                self.instance.cover_img.save(cover_filename,
                                             File(open(tmp_cover_path)),
                                             save=True)
            except Exception as e:
                logger.warn('Error saving cover image %s: %s' %
                            (cover_filename, str(e)))
            finally:
                # A second tmp cover file is generated during form validation.
                second_tmp = form_list[0].cleaned_data['cover_path']
                # Delete temporary cover files.
                os.remove(tmp_cover_path)
                if second_tmp:
                    os.remove(second_tmp)

        return redirect(self.instance.get_absolute_url())


@login_required
def add_language(request):
    return handle_pop_add(request, AddLanguageForm, 'language')


class AuthorDetailView(DetailView):
    model = Author

    def get_context_data(self, **kwargs):
        context = super(AuthorDetailView, self).get_context_data(**kwargs)
        context['book_list'] = self.object.books.all()
        # context['book_list'] = Book.objects.filter(authors=self.object)
        context['allow_user_comments'] = settings.ALLOW_USER_COMMENTS

        return context


class AuthorEditView(UpdateView):
    model = Author
    form_class = AuthorEditForm

    def get_context_data(self, **kwargs):
        context = super(AuthorEditView, self).get_context_data(**kwargs)
        context.update({'action': 'edit'})
        return context

    def get_success_url(self):
        return reverse('author_detail', kwargs={'pk': self.object.pk})


class AuthorListView(PaginationMixin, ListView):
    model = Author
    context_object_name = "authors"
    paginate_by = settings.BOOKS_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super(AuthorListView, self).get_context_data(**kwargs)
        context['allow_user_comments'] = settings.ALLOW_USER_COMMENTS
        context['q'] = self.request.GET.get('q')
        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            queryset = self.model.objects.filter(name__icontains=query)
        else:
            queryset = Author.objects.all()
        return queryset


# https://stackoverflow.com/questions/16937076/how-does-one-use-a-custom-widget-with-a-generic-updateview-without-having-to-red
# https://stackoverflow.com/questions/17052701/problems-integrating-django-autocomplete-light-with-django-taggit

class BookEditView(UpdateView):
    model = Book
    form_class = BookEditForm

    def get_context_data(self, **kwargs):
        context = super(BookEditView, self).get_context_data(**kwargs)
        context.update({'action': 'edit'})

        return context


class BookDeleteView(DeleteView):
    model = Book
    success_url = '/'


class BookDetailView(View):
    # model = Book

    def get(self, request, *args, **kwargs):
        view = BookDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = BookAddTags.as_view()
        return view(request, *args, **kwargs)

    # def get_context_data(self, **kwargs):
    # context = super(BookDetailView, self).get_context_data(**kwargs)
    # context['form'] = BookAddTagsForm()
    # context.update({'allow_user_comments': settings.ALLOW_USER_COMMENTS})
    #
    # return context


class BookAddTags(SingleObjectMixin, FormView):
    template_name = 'books/book_detail.html'
    form_class = BookAddTagsForm
    model = Book

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden()
        self.object = self.get_object()
        return super(BookAddTags, self).post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.pk})


class BookDisplay(DetailView):
    model = Book

    def get_context_data(self, **kwargs):
        context = super(BookDisplay, self).get_context_data(**kwargs)
        context['form'] = BookAddTagsForm()
        context.update({'allow_user_comments': settings.ALLOW_USER_COMMENTS})
        return context


def download_book(request, book_id):
    """Return the epub file for a Book with `book_id` using sendfile. It
    returns the file stored in media by Django.
    TODO: decide if in some cases the original file should be returned instead.
    TODO: currently the downloaded file name is the same as the stored file.
    Decide if it should be standardized to something else instead.

    :param request:
    :param book_id:
    :returns:
    """
    book = get_object_or_404(Book, pk=book_id)
    # filename = os.path.join(settings.MEDIA_ROOT, book.original_path.name)
    # filename = unicode(os.path.abspath(book.original_path))  # unicode?
    filename = book.book_file.path

    # TODO, currently the downloads counter is incremented when the
    # download is requested, without knowing if the file sending was
    # successful:
    book.downloads += 1
    book.save()

    return sendfile(request, filename, attachment=True)


def tags(request, qtype=None, group_slug=None):
    """

    :param request:
    :param qtype:
    :param group_slug:
    :return:
    """
    context = {'list_by': 'by-tag'}

    tag_list = Tag.objects.all().annotate(count=Count('book'))

    if group_slug is not None:
        tag_group = get_object_or_404(TagGroup, slug=group_slug)
        context.update({'tag_group': tag_group})

        # TODO: find a way of performing the previous django-tagging
        # get_for_object(tag_group) using django-taggit. Currently it just
        # returns all the tags, as a quick hack for avoiding problems, but it
        # is the *wrong* behaviour.
        # context.update({'tag_list': Tag.objects.get_for_object(tag_group)})
        context.update({'tag_list': tag_list})
    else:
        context.update({'tag_list': tag_list})

    tag_groups = TagGroup.objects.all()
    context.update({'tag_group_list': tag_groups})

    # Return OPDS Atom Feed:
    if qtype == 'feed':
        catalog = generate_tags_catalog(context['tag_list'])
        return HttpResponse(catalog, content_type='application/atom+xml')

    # Return HTML page:
    return render(request, 'books/tag_list.html', context)


def tags_listgroups(request):
    tag_groups = TagGroup.objects.all()
    catalog = generate_taggroups_catalog(tag_groups)
    return HttpResponse(catalog, content_type='application/atom+xml')


def _book_list(request, queryset, qtype=None, list_by='latest', **kwargs):
    """
    Filter the books, paginate the result, and return either a HTML
    book list, or a atom+xml OPDS catalog.
    """
    q = request.GET.get('q')
    search_all = request.GET.get('search-all') == 'on'
    search_title = request.GET.get('search-title') == 'on'
    search_author = request.GET.get('search-author') == 'on'

    if not request.user.is_authenticated():
        queryset = queryset.filter(a_status=settings.BOOK_PUBLISHED)

    published_count = Book.objects.\
        filter(a_status=settings.BOOK_PUBLISHED).count()
    unpublished_count = Book.objects.\
        exclude(a_status=settings.BOOK_PUBLISHED).count()

    # If no search options are specified, assumes search all, the
    # advanced search will be used:
    if not search_all and not search_title and not search_author:
        search_all = True

    # If search queried, modify the queryset with the result of the
    # search:
    if q is not None:
        if search_all:
            queryset = advanced_search(queryset, q)
        else:
            queryset = simple_search(queryset, q,
                                     search_title, search_author)

    paginator = Paginator(queryset, settings.BOOKS_PER_PAGE)
    page = int(request.GET.get('page', '1'))

    try:
        page_obj = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page_obj = paginator.page(paginator.num_pages)

    # Build the query string:
    qstring = page_qstring(request)

    # Return OPDS Atom Feed:
    if qtype == 'feed':
        catalog = generate_catalog(request, page_obj)
        return HttpResponse(catalog, content_type='application/atom+xml')

    # Return HTML page:
    extra_context = dict(kwargs)
    extra_context.update({
        'book_list': page_obj.object_list,
        'published_books': published_count,
        'unpublished_books': unpublished_count,
        'q': q,
        'paginator': paginator,
        'page_obj': page_obj,
        'search_title': search_title,
        'search_author': search_author, 'list_by': list_by,
        'qstring': qstring,
        'allow_public_add_book': settings.ALLOW_PUBLIC_ADD_BOOKS,
        'allow_user_comments': settings.ALLOW_USER_COMMENTS,
    })

    return render(request, 'books/book_list2.html', extra_context)


def home(request):
    return redirect('latest')


def root(request, qtype=None):
    """Return the root catalog for navigation

    :param request:
    :param qtype:
    :returns:
    """
    root_catalog = generate_root_catalog()
    return HttpResponse(root_catalog, content_type='application/atom+xml')


def authors(request, qtype=None):
    queryset = authors.books.all()
    return _book_list(request, queryset, qtype, list_by='authors')


def latest(request, qtype=None):
    queryset = Book.objects.all()
    return _book_list(request, queryset, qtype, list_by='latest')


def by_title(request, qtype=None):
    queryset = Book.objects.all().order_by('title')
    return _book_list(request, queryset, qtype, list_by='by-title')


def by_author(request, qtype=None):
    queryset = Book.objects.all().order_by('authors')
    return _book_list(request, queryset, qtype, list_by='by-author')


def by_tag(request, tag, qtype=None):
    """ displays a book list by the tag argument
    :param request:
    :param tag:
    :param qtype:
    :returns:
    """
    # get the Tag object
    tag_instance = Tag.objects.get(name=tag)

    # if the tag does not exist, return 404
    if tag_instance is None:
        raise Http404()

    # Get a list of books that have the requested tag
    queryset = Book.objects.filter(tags=tag_instance)
    return _book_list(request, queryset, qtype, list_by='by-tag',
                      tag=tag_instance)


def most_downloaded(request, qtype=None):
    queryset = Book.objects.all().order_by('-downloads')
    return _book_list(request, queryset, qtype, list_by='most-downloaded')
