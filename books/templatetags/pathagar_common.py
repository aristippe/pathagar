from django import template
from django.conf import settings
from django.core.urlresolvers import reverse


register = template.Library()

RSS_URL_MAP = {'latest': 'latest_feed',
               'by-title': 'by_title_feed',
               'by-author': 'by_author_feed',
               'by-tag': 'by_tag_feed',
               'most-downloaded': 'most_downloaded_feed',
               'tags': 'tags_feed'
               }


def can_upload(user):
    """Return True if the user has upload permissions, taking into account
    Pathagar settings and the User.

    TODO: if we switch to a Django group/permission system, this is probably
    better done directly checking permissions.
    """
    if settings.ALLOW_PUBLIC_ADD_BOOKS:
        return True
    if user.is_authenticated():
        if settings.ALLOW_USER_EDIT or user.is_staff:
            return True
    return False


def rss_url(list_by, tag=None, q=''):
    """Return the RSS feed URL based on the `link_by` context variable. The
    GET parameters, if a query is performed, are included as well.
    """
    url_name = RSS_URL_MAP.get(list_by, 'latest')
    if url_name == 'by_tag_feed':
        # TODO: probably 'by_tag' and 'tags' are conflicting on urls.py.
        if tag:
            url = reverse(url_name, args=[tag.name])
        else:
            url = reverse('tags_feed')
    else:
        url = reverse(url_name)
    return '%s%s' % (url,
                     ('?q=%s' % str(q)) if q else '')


register.filter('can_upload', can_upload)
register.simple_tag(rss_url, name='rss_url')
