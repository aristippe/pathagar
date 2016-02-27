from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.exceptions import ValidationError

import os
import sys
import logging

from django.conf import settings

from books import models
from books.epub import Epub
from books.storage import LinkableFile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_epubs_paths(paths):
    """Return a list of paths for potential EPUB(s) from a list of file and
    directory names. The returned list contains only files with the '.epub'
    extension, traversing the directories recursively.

    :param paths:
    :return:
    """

    def validate_and_add(path, filenames):
        """Check that the `path` has an '.epub' extension, convert it to
        absolute and add it to `filenames` if not already imported and not
        present already in order to preserve the ordering.

        :param path:
        :param filenames:
        """
        if os.path.splitext(path)[1] == '.epub':
            filename = os.path.abspath(path)
            if filename not in filenames:
                if not models.Book.objects.filter(
                        original_path=filename).exists():
                    filenames.append(filename)

    print "Finding new ePubs ..."
    filenames = []
    for path in paths:
        if os.path.isdir(path):
            # path is a directory: traverse and add *.epub
            for root, _, files in os.walk(path):
                for name in files:
                    validate_and_add(os.path.join(root, name), filenames)
        elif os.path.isfile(path):  # Implicitly checks that 'path' exists.
            # path is a file: add if *.epub.
            validate_and_add(path, filenames)

    return filenames


class Command(BaseCommand):
    help = 'Import ePubs from the local file system into the database.'

    def add_arguments(self, parser):
        # Positional arguments.
        parser.add_argument(
            'item', nargs='+',
            type=lambda s: s.decode(sys.getfilesystemencoding()),
            help=("A file with '.epub' extension or a directory (in which "
                  "case it is traversed recursively, adding all the files "
                  "with '.epub' extension)."))

        # Named (optional) arguments.
        parser.add_argument(
            '--link', '-l',
            action='store_true',
            dest='use_symlink',
            default=False,
            help='Use symbolic links instead of copying the files.')

    def handle(self, *args, **options):
        epub_filenames = get_epubs_paths(options['item'])

        if not epub_filenames:
            raise CommandError('No .epub files found on the specified paths.')

        # Keep track of some basic stats.
        counter = {'success': 0, 'fail': 0}
        width = len(str(len(epub_filenames)))
        self.stdout.write('Importing %s items ...' % len(epub_filenames))

        for i, filename in enumerate(epub_filenames):
            self.stdout.write(self.style.HTTP_INFO(
                '[{i: {width}}/{total: {width}}] {f}'.format(
                    i=i,
                    total=len(epub_filenames),
                    width=width,
                    f=filename)))

            success = True
            try:
                success = self.process_epub(filename, options['use_symlink'])
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    'Unhandled exception while importing:\n%s' % e))
                success = False

            if success:
                counter['success'] += 1
                self.stdout.write(self.style.NOTICE('File imported'))
            else:
                counter['fail'] += 1
                self.stdout.write(self.style.NOTICE('File NOT imported'))
            self.stdout.write('')

        self.stdout.write('{} files imported, {} files not imported.'.format(
            counter['success'], counter['fail']))

    def process_epub(self, filename, use_symlink=False):
        """Import a single EPUB from `filename`, creating a new `Book` based
        on the information parsed from the epub.

        :param filename: ePub file to process
        :param use_symlink: symlink ePub to FileField or process normally
        :return: success result
        """

        # Try to parse the epub file, extracting the relevant info.
        info_dict = {}
        tmp_cover_path = None
        try:
            epub = Epub(filename)
            epub.get_info()
            # Get the information we need for creating the Model.
            info_dict, authors, publishers, tmp_cover_path, subjects = \
                epub.as_model_dict()
            assert info_dict
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                "Error while parsing '%s':\n%s" % (filename, unicode(e))))

            # TODO: this is not 100% reliable yet. Further modifications to
            # epub.py are needed.
            try:
                if tmp_cover_path:
                    os.remove(tmp_cover_path)
                # close() can fail itself it _zobject failed to be initialized.
                epub.close()
            except:
                pass
            return False

        # Prepare some model fields that require extra care.
        # Language (dc_language).
        try:
            language = models.Language.objects.get_or_create_by_code(
                info_dict['dc_language']
            )
            info_dict['dc_language'] = language
        except:
            info_dict['dc_language'] = None

        # Original filename (original_path).
        info_dict['original_path'] = filename
        # Published status (a_status).
        info_dict['a_status'] = models.Status.objects.get(
            status=settings.DEFAULT_BOOK_STATUS)

        # Create and save the Book.
        try:
            # Prepare the Book.
            book = models.Book(**info_dict)
            # Use a symlink or copy the file depending on options.
            if use_symlink:
                f = LinkableFile(open(filename))
            else:
                f = File(open(filename))
            book.book_file.save(os.path.basename(filename), f, save=False)
            book.file_sha256sum = models.sha256_sum(book.book_file)

            # Validate and save.
            book.full_clean()
            book.save()

            # Handle info that needs existing book instance thru book.save.
            # authors, publishers, cover, and tags

            # Add authors
            if authors:
                for author in authors:
                    if author is not None:
                        author_split = author.replace(
                            ' and ', ';').replace('&', ';').split(';')
                        for auth in author_split:
                            auth = auth.strip()
                            self.stdout.write(self.style.NOTICE(
                                'Found author: %s' % auth))
                            try:
                                author = models.Author.objects.get(name=auth)
                            except:
                                author = models.Author(name=auth)
                                author.save()
                            book.authors.add(author)

            # Add publishers
            if publishers:
                for publisher in publishers:
                    self.stdout.write(self.style.NOTICE(
                        'Found publisher: "%s"' % publisher))
                    try:
                        publisher = models.Publisher.objects.get(
                            name=publisher)
                    except:
                        publisher = models.Publisher(name=publisher)
                        publisher.save()
                    book.publishers.add(publisher)

            # Add cover image (cover_image). It is handled here as the filename
            # depends on instance.pk (which is only present after Book.save()).
            if tmp_cover_path:
                try:
                    cover_filename = '%s%s' % (
                        book.pk, os.path.splitext(tmp_cover_path)[1]
                    )
                    book.cover_img.save(cover_filename,
                                        File(open(tmp_cover_path)),
                                        save=True)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(
                        'Error while saving cover image %s:\n%s' % (
                            tmp_cover_path, str(e))))
                    tmp_cover_path = None

            # Add subjects as tags
            if subjects:
                for subject in subjects:
                    # workaround for ePubs with description as subject
                    if len(subject) <= 80:
                        subject_split = subject.replace('/', ',') \
                            .replace(';', ',') \
                            .replace(':', '') \
                            .replace('\n', ',') \
                            .replace(' ,', ',') \
                            .split(',')
                        for tag in subject_split:
                            tag = tag.encode("utf-8").lower().strip()
                            self.stdout.write(self.style.NOTICE(
                                'Found subject (tag): %s'
                                % tag))
                            book.tags.add(tag)
        except Exception as e:
            # Delete .epub file in media/, if `book` is a valid object.
            try:
                if os.path.isfile(book.book_file.path):
                    os.remove(book.book_file.path)
            except:
                pass

            if isinstance(e, ValidationError) and 'already exists' in str(e):
                self.stdout.write(self.style.WARNING(
                    'The book (%s) was not saved because the file already '
                    'exists in the database:\n%s' % (filename, str(e))))
                return False
            else:
                # TODO: check for possible risen exceptions at a finer grain.
                raise e
        finally:
            # Delete the temporary files.
            epub.close()
            if tmp_cover_path:
                os.remove(tmp_cover_path)

        return True
