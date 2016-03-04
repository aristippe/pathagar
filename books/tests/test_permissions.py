# -*- coding: utf-8 -*-
from collections import namedtuple
from itertools import product
import os
import shutil
import tempfile

from mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import File
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.test import TestCase

from books import models
import sample_epubs


user = namedtuple('user_tuple', ('username', 'password', 'email'))
result = namedtuple('result', ('admin', 'user', 'anonymous'))


class PermissionsTestCase(TestCase):
    fixtures = ['initial_data.json']

    USERS = [user('admin', 'adminpass', 'adminemail'),
             user('user', 'userpass', '')]

    # Base list of the views config, when all the variables are set to False
    VIEWS_BASE = {
        'home': (result(reverse('latest'), reverse('latest'), False), []),
        # Book list
        'latest': (result(200, 200, False), []),
        'by_title': (result(200, 200, False), []),
        'by_author': (result(200, 200, False), []),
        # 'authors': (result(200, 200, False), ['Tag1']), Wrong parameter?
        'by_tag': (result(200, 200, False), ['Tag1']),
        'most_downloaded': (result(200, 200, False), []),

        # Feeds
        # TODO: currently seems feeds are broken
        # 'root_feed': (result(200, 200, False), []),
        # 'latest_feed': (result(200, 200, False), []),
        # 'by_title_feed': (result(200, 200, False), []),
        # 'by_author_feed': (result(200, 200, False), []),
        # 'by_tag_feed': (result(200, 200, False), ['Tag1']),
        # 'most_downloaded_feed': (result(200, 200, False), []),

        # Book handling
        'book_add': (result(200, 200, False), []),
        'book_detail': (result(200, 200, False), [1]),
        'book_edit': (result(200, 200, False), [1]),
        'book_delete': (result(200, 200, False), [1]),
        'book_download': (result(200, 200, False), [1]),

        # TODO: add rest of the urls
    }

    def _get_view_configuration(self,
                                allow_public_add_books, allow_public_browse):
        """Convenience function for getting a list of the views along with
        the expected results for each kind of user, depending on the Pathagar
        defined settings.
        """
        ret = self.VIEWS_BASE.copy()
        if allow_public_add_books:
            # TODO: allow_public_add does not make much sense without
            # allow_public_browse
            ret['book_add'] = (result(200, 200, 200), [])
        if allow_public_browse:
            ret['home'] = (result(reverse('latest'), reverse('latest'),
                                  reverse('latest')), [])
            # Book list
            ret['latest'] = (result(200, 200, 200), [])
            ret['by_title'] = (result(200, 200, 200), [])
            ret['by_author'] = (result(200, 200, 200), [])
            ret['by_tag'] = (result(200, 200, 200), ['Tag1'])
            ret['most_downloaded'] = (result(200, 200, 200), [])

            # Feeds
            # ret['root_feed'] = (result(200, 200, 200), [])
            # ret['latest_feed'] = (result(200, 200, 200), [])
            # ret['by_title_feed'] = (result(200, 200, 200), [])
            # ret['by_author_feed'] = (result(200, 200, 200), [])
            # ret['by_tag_feed'] = (result(200, 200, 200), ['Tag1'])
            # ret['most_downloaded_feed'] = (result(200, 200, 200), [])

            # Book handling
            # Only view and download.
            ret['book_detail'] = (result(200, 200, 200), [1])
            ret['book_download'] = (result(200, 200, 200), [1])

        return ret

    def get_and_assert_results(self, view, args, user, expected_results):
        """Get a `view` via the client, comparing the response with the
        expected result for the `user` via an assertion.
        """
        # Get the expected result based on the user.
        if user:
            if user.is_superuser:
                result = expected_results.admin
            else:
                result = expected_results.user
        else:
            result = expected_results.anonymous

        # Request the view.
        print ' %s %s -> %s' % (view, args, result)
        response = self.client.get(reverse(view, args=args))

        # Make assertions on the result.
        if result and isinstance(result, int):
            # Check the response status code directly.
            self.assertEqual(response.status_code, result)
        elif result is False:
            # User does not have permission, check for redirect to login.
            self.assertRedirects(response,
                                 "%s?next=%s" % (settings.LOGIN_URL,
                                                 reverse(view, args=args)))
        else:
            self.assertRedirects(response, result)

    def setUp(self):
        # Create an admin and a regular user.
        self.users = []
        for f, user in zip([User.objects.create_superuser,
                            User.objects.create_user],
                           self.USERS):
            user_instance = f(username=user.username,
                              password=user.password,
                              email=user.email)
            user_instance.save()
            self.users.append((user, user_instance))

        # Create a temporary dir to replace MEDIA_ROOT.
        self.tmp_media_root = tempfile.mkdtemp()

        # Start the mocker which replaces MEDIA_ROOT with the tmp folder.
        # This should have been accomplished via test.utils.override_settings,
        # but seems that it does not work when using a custom storage.
        # TODO: check if new Django versions fix this, and get rid of mock.
        self.path_patcher = patch.object(
            FileSystemStorage, 'path',
            lambda instance, name: os.path.join(self.tmp_media_root, name))
        self.mock_path = self.path_patcher.start()

        # Create some sample data.
        author = models.Author(name='Author1')
        author.save()
        epub = sample_epubs.EPUBS_VALID[0]
        book = models.Book(title='Book1',
                           a_status=models.Status.objects.get(pk=1),
                           mimetype='foo')
        book.save()
        book.book_file.save(epub.filename,
                            File(open(epub.fullpath, 'r')),
                            save=False)
        book.authors.add(author)
        book.tags.add('Tag1')
        book.save()

    def tearDown(self):
        # Stop the mocker.
        self.path_patcher.stop()
        # Remove the temporary MEDIA_ROOT file.
        shutil.rmtree(self.tmp_media_root)

    def test_permissions_false_true(self):
        for allow_add, allow_browse in product([False, True], repeat=2):
            # Retrieve the view permissions configuration for the combination
            # of Pathagar settings, modifying SETTINGS accordingly.
            print '\nModifying settings ...'
            print (' ALLOW_PUBLIC_ADD_BOOKS = %s\n'
                   ' ALLOW_PUBLIC_BROWSE = %s' % (allow_add, allow_browse))
            views_config = self._get_view_configuration(allow_add,
                                                        allow_browse)
            print 'Testing views ...'

            with self.settings(ALLOW_PUBLIC_ADD_BOOKS=allow_add,
                               ALLOW_PUBLIC_BROWSE=allow_browse):
                # Loop through the available users.
                for user, user_instance in [self.users[0],
                                            self.users[1],
                                            (None, None)]:
                    # Logout and login as the desired user.
                    self.client.logout()
                    if user:
                        self.client.login(username=user.username,
                                          password=user.password)
                    print ' [%s]' % (user_instance or 'anonymous')

                    # Test each view
                    for view, (results, args) in views_config.iteritems():
                        self.get_and_assert_results(view,
                                                    args,
                                                    user_instance,
                                                    results)
                    print
