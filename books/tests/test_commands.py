import filecmp
import os
import tempfile
import shutil

from mock import patch

from django.core.files.storage import FileSystemStorage
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TransactionTestCase
from django.utils.crypto import get_random_string

from books import models
import sample_epubs


class CommandAddEpubTest(TransactionTestCase):
    fixtures = ['initial_data.json']

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
        call_command('addepub', *src_epubs, skip_original_path=True)

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
        call_command('addepub', *src_epubs, use_symlink=True,
                     skip_original_path=True)

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

    def test_addepub_skipping(self):
        """Test the `addepub` `--ignore-original-path` flag.
        """
        # Try to import all the valid epubs.
        src_epubs = [epub.fullpath for epub in sample_epubs.EPUBS_VALID]
        call_command('addepub', *src_epubs)
        self.assertEqual(models.Book.objects.count(),
                         len(sample_epubs.EPUBS_VALID))

        # Try to import them again, skipping them during get_epub_paths
        # (default behaviour), which should raise a CommandError.
        src_epubs = [epub.fullpath for epub in sample_epubs.EPUBS_VALID]
        with self.assertRaises(CommandError):
            call_command('addepub', *src_epubs)

        # Try to import them again, not skipping them, which should result
        # in all of them marked as duplicates due to SHA and not imported.
        src_epubs = [epub.fullpath for epub in sample_epubs.EPUBS_VALID]
        call_command('addepub', *src_epubs, skip_original_path=False)
        self.assertEqual(models.Book.objects.count(),
                         len(sample_epubs.EPUBS_VALID))


class CommandResyncTest(TransactionTestCase):
    fixtures = ['initial_data.json']

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

    def _copy_to_newtmp(self, epubs, rename=False):
        """Create a new temporary file, and copy `epubs` there, optionally
        renaming them.
        Returns the temporary dir.
        """
        new_dir = tempfile.mkdtemp()
        get_random_string
        for epub in epubs:
            if rename:
                new_name = '%s.epub' % get_random_string()
            else:
                new_name = epub.filename
            # Copy the file.
            shutil.copy2(epub.fullpath, os.path.join(new_dir, new_name))

        print 'Working on %s ...' % new_dir
        return new_dir

    def test_addepub_nolink(self):
        """Test the `resync` command.
        """
        # Import the valid epubs, in copy mode.
        src_epubs = [epub.fullpath for epub in sample_epubs.EPUBS_VALID]
        call_command('addepub', *src_epubs)

        # Hand pick some epubs for convenience.
        epub_a = sample_epubs.EPUBS_VALID[0]
        epub_b = sample_epubs.EPUBS_VALID[1]
        test_epubs = [epub_a, epub_b]

        # Test always-link strategy with epub_a.
        new_source_dir = self._copy_to_newtmp(test_epubs)
        call_command('resync',
                     os.path.join(new_source_dir, epub_a.filename),
                     replace_strategy='always-link')

        # Check that original_path has been updated, and file is a link
        book = models.Book.objects.get(book_file__endswith=epub_a.filename)
        self.assertEqual(book.original_path,
                         os.path.join(new_source_dir, epub_a.filename))
        self.assertTrue(os.path.islink(os.path.join(self.tmp_media_root,
                                                    book.book_file.path)))

        # Test always-copy strategy with epub_a (which now is a link).
        call_command('resync',
                     os.path.join(new_source_dir, epub_a.filename),
                     replace_strategy='always-copy')
        # Check that original_path has been updated, and file is *not* a link
        book = models.Book.objects.get(book_file__endswith=epub_a.filename)
        self.assertEqual(book.original_path,
                         os.path.join(new_source_dir, epub_a.filename))
        self.assertFalse(os.path.islink(os.path.join(self.tmp_media_root,
                                                     book.book_file.path)))

        # Set epub_b to a link, and delete tmp_dir.
        call_command('resync',
                     os.path.join(new_source_dir, epub_b.filename),
                     replace_strategy='always-link')
        shutil.rmtree(new_source_dir)

        # Test original strategy with both epubs. At this stage, epub_a->copy,
        # epub_b->link, and it should stay that way after the resync.
        new_source_dir = self._copy_to_newtmp(test_epubs)
        call_command('resync', new_source_dir)
        # Check original_paths and copies/links.
        models.Book.objects.update()
        book_a = models.Book.objects.get(book_file__endswith=epub_a.filename)
        book_b = models.Book.objects.get(book_file__endswith=epub_b.filename)
        book_b = models.Book.objects.get(pk=book_b.pk)
        self.assertEqual(book_a.original_path,
                         os.path.join(new_source_dir, epub_a.filename))
        self.assertEqual(book_b.original_path,
                         os.path.join(new_source_dir, epub_b.filename))
        self.assertFalse(os.path.islink(os.path.join(self.tmp_media_root,
                                                     book_a.book_file.path)))
        self.assertTrue(os.path.islink(os.path.join(self.tmp_media_root,
                                                    book_b.book_file.path)))

        # Cleanup.
        shutil.rmtree(new_source_dir)
