import filecmp
import os
import tempfile
import shutil

from mock import patch

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.management import call_command
from django.test import TransactionTestCase

from books import models


# TODO: move these variables to a separate module, for using in other tests;
# add more sample ebooks, and tidy up the tree structure when refactoring.
RSRC_DIR = os.path.abspath(os.path.join(settings.CUR_DIR,
                                        'resources/epubsamples'))

EPUBS = {'epub30-spec': 'epub30-spec.epub',
         'figure-gallery': 'figure-gallery-bindings.epub',
         'not-epub': 'not-an-epub.epub',
         'not-epub-zip': 'not-an-epub-but-a-zip.epub'}

EPUBS_ALL = [key for key in EPUBS.iterkeys()]
EPUBS_VALID = ('epub30-spec', 'figure-gallery')
EPUBS_NOT_VALID = ('not-epub', 'not-epub-zip')
EPUBS_COVER = ('figure-gallery',)
EPUBS_NOT_COVER = ('epub30-spec',)


def _src_epub(name):
    """Return the absolute path of a sample epub. `name` should be a valid
    key in EPUBS.
    """
    return os.path.join(RSRC_DIR, EPUBS[name])


class CommandAddEpubTest(TransactionTestCase):
    def setUp(self):
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

    def tearDown(self):
        # Stop the mocker.
        self.path_patcher.stop()
        # Remove the temporary MEDIA_ROOT file.
        shutil.rmtree(self.tmp_media_root)

    def test_addepub_nolink(self):
        """Test the `addepub` command in "copy files" mode (default).
        """
        # Try to import all the sample epubs.
        src_epubs = [_src_epub(i) for i in EPUBS_ALL]
        call_command('addepub', *src_epubs)

        # Get the list of output files.
        media_books = os.listdir(os.path.join(self.tmp_media_root, 'books'))
        media_covers = os.listdir(os.path.join(self.tmp_media_root, 'covers'))

        # Make assertions on the VALID epubs.
        self.assertEqual(models.Book.objects.count(), len(EPUBS_VALID))
        for key in EPUBS_VALID:
            # Assert the Book with that file exists on the DB.
            qs = models.Book.objects.filter(book_file__endswith=EPUBS[key])
            self.assertEqual(qs.count(), 1)

            # Assert some properties of the Book.
            book = qs.get()
            self.assertEqual(book.original_path, _src_epub(key))

            if key in EPUBS_COVER:
                self.assertTrue(book.cover_img)
                self.assertTrue([f for f in media_covers
                                 if f.startswith('%s.' % book.pk)])
            else:
                self.assertFalse(book.cover_img)

            # Assert that the file is on media, is copied, and equal to source.
            self.assertIn(EPUBS[key], media_books)
            self.assertFalse(os.path.islink(book.book_file.path))
            self.assertTrue(filecmp.cmp(book.book_file.path, _src_epub(key)))

        # Make assertions on the NOT_VALID epubs.
        for key in EPUBS_NOT_VALID:
            # Assert no Book with that file exists on the DB.
            qs = models.Book.objects.filter(book_file__endswith=EPUBS[key])
            self.assertFalse(qs.exists())

            # Assert that the file is not on media.
            self.assertNotIn(EPUBS[key], media_books)

        # Make assertions on the files as a whole.
        self.assertEqual(len(media_books), len(EPUBS_VALID))
        self.assertEqual(len(media_covers), len(EPUBS_COVER))
