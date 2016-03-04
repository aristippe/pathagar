from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from books import views
from books import forms
from books.decorators import (login_or_public_browse_required,
                              login_or_public_add_book_required)

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
    url(r'^authors/(?P<tag>.+)/$',
        login_or_public_browse_required(views.authors),
        {}, 'authors'),
    url(r'^tags/(?P<tag>.+)/$', login_or_public_browse_required(views.by_tag),
        {}, 'by_tag'),
    url(r'^by-popularity/$',
        login_or_public_browse_required(views.most_downloaded),
        {}, 'most_downloaded'),

    # Tag groups:
    url(r'^tags/groups.atom$',
        login_or_public_browse_required(views.tags_listgroups),
        {}, 'tags_listgroups'),

    # Book list Atom:
    url(r'^catalog.atom$', views.root,
        {'qtype': u'feed'}, 'root_feed'),
    url(r'^latest.atom$', views.latest,
        {'qtype': u'feed'}, 'latest_feed'),
    url(r'^by-title.atom$', views.by_title,
        {'qtype': u'feed'}, 'by_title_feed'),
    url(r'^by-author.atom$', views.by_author,
        {'qtype': u'feed'}, 'by_author_feed'),
    url(r'^tags/(?P<tag>.+).atom$', views.by_tag,
        {'qtype': u'feed'}, 'by_tag_feed'),
    url(r'^by-popularity.atom$', views.most_downloaded,
        {'qtype': u'feed'}, 'most_downloaded_feed'),

    # Tag groups:
    url(r'^tags/groups/(?P<group_slug>[-\w]+)/$', views.tags,
        {}, 'tag_groups'),

    url(r'^tags/groups/(?P<group_slug>[-\w]+).atom$', views.tags,
        {'qtype': u'feed'}, 'tag_groups_feed'),

    # Tag list:
    url(r'^tags/$', views.tags, {}, 'tags'),
    url(r'^tags.atom$', views.tags, {'qtype': u'feed'}, 'tags_feed'),

    # Add, view, edit and remove books:
    url(r'^book/add$',
        login_or_public_add_book_required(views.AddBookWizard.as_view(
            [forms.BookUploadForm, forms.BookMetadataForm])),
        name='book_add'),
    url(r'^book/(?P<pk>\d+)/view$',
        login_or_public_browse_required(views.BookDisplay.as_view()),
        name='book_detail'),
    url(r'^book/(?P<pk>\d+)/edit$',
        login_required(views.BookEditView.as_view()),
        name='book_edit'),
    url(r'^book/(?P<pk>\d+)/remove$',
        login_required(views.BookDeleteView.as_view()),
        name='book_delete'),

    url(r'^author/(?P<pk>\d+)/$',
        login_required(views.AuthorDetailView.as_view()),
        name='author_detail'),
    url(r'^authors/$',
        login_required(views.AuthorListView.as_view()),
        name='author_list'),
    url(r'^author/(?P<pk>\d+)/edit$',
        login_required(views.AuthorEditView.as_view()),
        name='author_edit'),

    url(r'^book/(?P<book_id>\d+)/download$',
        login_or_public_browse_required(views.download_book),
        name='book_download'),

    # Auto-complete for book model m2m fields
    url(
        'author-autocomplete/$',
        login_required(views.AuthorAutocomplete.as_view()),
        name='author-autocomplete',
    ),
    url(
        'book-autocomplete/$',
        login_required(views.BookAutocomplete.as_view()),
        name='book-autocomplete',
    ),
    url(
        'publisher-autocomplete/$',
        login_required(views.PublisherAutocomplete.as_view()),
        name='publisher-autocomplete',
    ),
    url(
        'tags-autocomplete/$',
        login_required(views.TagAutocomplete.as_view()),
        name='tags-autocomplete',
    ),

    # Comments
    url(r'^comments/', include('django_comments.urls')),

    # Add language:
    url(r'^add/(?:dc_language|language)/$', views.add_language),

    # Auth login and logout:
    url(r'^accounts/', include('userena.urls')),
    url(r'^signin/',
        'userena.views.signin',
        {'template_name': 'signin_form.html'},
        name="signin"),
    # url(r'^accounts/login/$', login, name='login'),
    # url(r'^accounts/logout/$', logout, name='logout'),

    # Admin:
    url(r'^admin/', include(admin.site.urls)),
]

# Serve static and media files directly on development server (DEBUG).
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
