from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from books import views
from books import forms
from books.decorators import (login_or_public_browse_required,
                              login_or_public_add_book_required,
                              staff_or_allow_user_edit)

admin.autodiscover()

urlpatterns = [
    # Book list:
    url(r'^$', login_or_public_browse_required(views.home),
        {}, 'home'),
    url(r'^latest/$', login_or_public_browse_required(views.latest),
        {}, 'latest'),
    url(r'^by-title/$', login_or_public_browse_required(views.by_title),
        {}, 'by_title'),
    url(r'^by-author/$', login_or_public_browse_required(views.by_author),
        {}, 'by_author'),
    url(r'^tags/(?P<tag>.+)/$', login_or_public_browse_required(views.by_tag),
        {}, 'by_tag'),
    url(r'^by-popularity/$',
        login_or_public_browse_required(views.most_downloaded),
        {}, 'most_downloaded'),

    # Tag groups:
    url(r'^tags/groups/(?P<group_slug>[-\w]+)/$', views.tags,
        {}, 'tag_groups'),
    url(r'^tags/groups/(?P<group_slug>[-\w]+).atom$', views.tags,
        {'qtype': u'feed'}, 'tag_groups_feed'),
    url(r'^tags/groups.atom$',
        login_or_public_browse_required(views.tags_listgroups),
        {}, 'tags_listgroups'),

    # Book list Atom:
    url(r'^catalog.atom$', login_or_public_browse_required(views.root),
        {'qtype': u'feed'}, 'root_feed'),
    url(r'^latest.atom$', login_or_public_browse_required(views.latest),
        {'qtype': u'feed'}, 'latest_feed'),
    url(r'^by-title.atom$', login_or_public_browse_required(views.by_title),
        {'qtype': u'feed'}, 'by_title_feed'),
    url(r'^by-author.atom$', login_or_public_browse_required(views.by_author),
        {'qtype': u'feed'}, 'by_author_feed'),
    url(r'^tags/(?P<tag>.+).atom$',
        login_or_public_browse_required(views.by_tag),
        {'qtype': u'feed'}, 'by_tag_feed'),
    url(r'^by-popularity.atom$',
        login_or_public_browse_required(views.most_downloaded),
        {'qtype': u'feed'}, 'most_downloaded_feed'),

    # Tag list:
    url(r'^tags/$', login_or_public_browse_required(views.tags),
        {}, 'tags'),
    url(r'^tags.atom$', login_or_public_browse_required(views.tags),
        {'qtype': u'feed'}, 'tags_feed'),

    # Book management and download:
    url(r'^book/add$',
        login_or_public_add_book_required(
            views.AddBookWizard.as_view([forms.BookUploadForm,
                                         forms.BookMetadataForm])),
        name='book_add'),
    url(r'^book/(?P<pk>\d+)/view$',
        login_or_public_browse_required(views.BookDisplay.as_view()),
        name='book_detail'),
    url(r'^book/(?P<pk>\d+)/edit$',
        staff_or_allow_user_edit()(views.BookEditView.as_view()),
        name='book_edit'),
    url(r'^book/(?P<pk>\d+)/remove$',
        staff_or_allow_user_edit()(views.BookDeleteView.as_view()),
        name='book_delete'),
    url(r'^book/(?P<book_id>\d+)/download$',
        login_or_public_browse_required(views.download_book),
        name='book_download'),

    # Author management:
    url(r'^author/(?P<pk>\d+)/$',
        login_or_public_browse_required(views.AuthorDetailView.as_view()),
        name='author_detail'),
    url(r'^authors/$',
        login_or_public_browse_required(views.AuthorListView.as_view()),
        name='author_list'),
    url(r'^author/(?P<pk>\d+)/edit$',
        staff_or_allow_user_edit()(views.AuthorEditView.as_view()),
        name='author_edit'),

    # Auto-complete for book model m2m fields
    url(
        'author-autocomplete/$',
        login_or_public_add_book_required(views.AuthorAutocomplete.as_view()),
        name='author_autocomplete',
    ),
    url(
        'book-autocomplete/$',
        login_or_public_add_book_required(views.BookAutocomplete.as_view()),
        name='book_autocomplete',
    ),
    url(
        'publisher-autocomplete/$',
        login_or_public_add_book_required(
            views.PublisherAutocomplete.as_view()),
        name='publisher_autocomplete',
    ),
    url(
        'tags-autocomplete/$',
        login_or_public_add_book_required(views.TagAutocomplete.as_view()),
        name='tags_autocomplete',
    ),

    # Comments
    url(r'^comments/', include('django_comments.urls')),

    # Auth login and logout:
    url(r'^accounts/', include('userena.urls')),

    # Admin:
    url(r'^admin/', include(admin.site.urls)),
]

# Serve static and media files directly on development server (DEBUG).
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
