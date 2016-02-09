import filecmp
import os
import tempfile
import shutil

from mock import patch

from django.core.files.storage import FileSystemStorage
from django.core.management import call_command
from django.test import TransactionTestCase

from books import models
import sample_epubs


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
        src_epubs = [epub.fullpath for epub in sample_epubs.EPUBS_ALL]
        call_command('addepub', *src_epubs)

        # Get the list of output files.
        media_books = os.listdir(os.path.join(self.tmp_media_root, 'books'))
        media_covers = os.listdir(os.path.join(self.tmp_media_root, 'covers'))

        # Make assertions on the VALID epubs.
        self.assertEqual(models.Book.objects.count(),
                         len(sample_epubs.EPUBS_VALID))
        for epub in sample_epubs.EPUBS_VALID:
            # Assert the Book with that file exists on the DB.
            qs = models.Book.objects.filter(book_file__endswith=epub.filename)
            self.assertEqual(qs.count(), 1)

            # Assert some properties of the Book.
            book = qs.get()
            self.assertEqual(book.original_path, epub.fullpath)

            if epub in sample_epubs.EPUBS_COVER:
                self.assertTrue(book.cover_img)
                self.assertTrue([f for f in media_covers
                                 if f.startswith('%s.' % book.pk)])
                self.assertFalse(os.path.islink(book.cover_img.path))
            else:
                self.assertFalse(book.cover_img)

            # Assert that the file is on media, is copied, and equal to source.
            self.assertIn(epub.filename, media_books)
            self.assertFalse(os.path.islink(book.book_file.path))
            self.assertTrue(filecmp.cmp(book.book_file.path, epub.fullpath))

        # Make assertions on the NOT_VALID epubs.
        for epub in sample_epubs.EPUBS_NOT_VALID:
            # Assert no Book with that file exists on the DB.
            qs = models.Book.objects.filter(book_file__endswith=epub.filename)
            self.assertFalse(qs.exists())

            # Assert that the file is not on media.
            self.assertNotIn(epub.filename, media_books)

        # Make assertions on the files as a whole.
        self.assertEqual(len(media_books), len(sample_epubs.EPUBS_VALID))
        self.assertEqual(len(media_covers), len(sample_epubs.EPUBS_COVER))

    def test_addepub_symlink(self):
        """Test the `addepub` command in "symbolic links" mode.
        """
        # Try to import all the sample epubs.
        src_epubs = [epub.fullpath for epub in sample_epubs.EPUBS_ALL]
        call_command('addepub', *src_epubs, use_symlink=True)

        # Get the list of output files.
        media_books = os.listdir(os.path.join(self.tmp_media_root, 'books'))
        media_covers = os.listdir(os.path.join(self.tmp_media_root, 'covers'))

        # Make assertions on the VALID epubs.
        self.assertEqual(models.Book.objects.count(),
                         len(sample_epubs.EPUBS_VALID))
        for epub in sample_epubs.EPUBS_VALID:
            # Assert the Book with that file exists on the DB.
            qs = models.Book.objects.filter(book_file__endswith=epub.filename)
            self.assertEqual(qs.count(), 1)

            # Assert some properties of the Book.
            book = qs.get()
            self.assertEqual(book.original_path, epub.fullpath)

            if epub in sample_epubs.EPUBS_COVER:
                self.assertTrue(book.cover_img)
                self.assertTrue([f for f in media_covers
                                 if f.startswith('%s.' % book.pk)])
                self.assertFalse(os.path.islink(book.cover_img.path))
            else:
                self.assertFalse(book.cover_img)

            # Assert that the file is on media, is linked, and equal to source.
            self.assertIn(epub.filename, media_books)
            self.assertTrue(os.path.islink(book.book_file.path))
            self.assertTrue(filecmp.cmp(book.book_file.path, epub.fullpath))

        # Make assertions on the NOT_VALID epubs.
        for epub in sample_epubs.EPUBS_NOT_VALID:
            # Assert no Book with that file exists on the DB.
            qs = models.Book.objects.filter(book_file__endswith=epub.filename)
            self.assertFalse(qs.exists())

            # Assert that the file is not on media.
            self.assertNotIn(epub.filename, media_books)

        # Make assertions on the files as a whole.
        self.assertEqual(len(media_books), len(sample_epubs.EPUBS_VALID))
        self.assertEqual(len(media_covers), len(sample_epubs.EPUBS_COVER))
