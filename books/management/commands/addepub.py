from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.exceptions import ValidationError

import os

from books import models
from books.epub import Epub


def get_epubs_paths(paths):
    """Return a list of paths for potential EPUB(s) from a list of file and
    directory names. The returned list contains only files with the '.epub'
    extension, traversing the directories recursively.
    """

    def validate_and_add(path, filenames):
        """Check that the `path` has an '.epub' extension, convert it to
        absolute and add it to `filenames` if not present already in order to
        preserve the ordering.
        """
        if os.path.splitext(path)[1] == '.epub':
            filename = os.path.abspath(path)
            if filename not in filenames:
                filenames.append(filename)

    filenames = []
    for path in paths:
        if os.path.isdir(path):
            # path is a directory: traverse and add *.epub
            for root, _, files in os.walk(path):
                for name in files:
                    validate_and_add(os.path.join(root, name), filenames)
        elif os.path.isfile(path):  # Implicitely checks that 'path' exists.
            # path is a file: add if *.epub.
            validate_and_add(path, filenames)

    return filenames


class Command(BaseCommand):
    # TODO: on Django 1.8+, optparse should be used.
    help = ("Import EPUBs from the local file system into the database. ITEMs "
            "can be either:\n"
            "- a single file with '.epub' extension.\n"
            "- a directory (in which case it is traversed recursively, "
            "adding all the files with '.epub' extension).")
    args = '<ITEM ITEM ...>'

    def handle(self, *args, **options):
        epub_filenames = get_epubs_paths(args)

        if not epub_filenames:
            raise CommandError('No .epub files found on the specified paths.')

        for filename in epub_filenames:
            success = True
            try:
                success = self.process_epub(filename)
            except Exception as e:
                print 'Unhandled exception while importing: %s' % e
                success = False

            if success:
                print 'File imported'
            else:
                print 'File NOT imported'

    def process_epub(self, filename):
        """Import a single EPUB from `filename`, creating a new `Book` based
        on the information parsed from the epub.
        """
        # TODO: move prints to logging.
        print '\nImporting %s' % filename

        # Try to parse the epub file, extracting the relevant info.
        info_dict = {}
        tmp_cover_path = None
        try:
            epub = Epub(filename)
            _ = epub.get_info()
            # Get the information we need for creating the Model.
            info_dict, tmp_cover_path = epub.as_model_dict()
            assert info_dict
        except Exception as e:
            print "Error while parsing '%s': %s" % (filename, unicode(e))

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
        # TODO: use DEFAULT_BOOK_STATUS instead of hard-coding.
        info_dict['a_status'] = models.Status.objects.get(status='Published')

        # Create and save the Book.
        try:
            # Prepare the Book.
            book = models.Book(**info_dict)
            book.book_file.save(os.path.basename(filename),
                                File(open(filename)),
                                save=False)
            book.file_sha256sum = models.sha256_sum(book.book_file)

            # Validate and save.
            book.full_clean()
            book.save()

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
                    print 'Error while saving cover image %s: %s' % (
                        tmp_cover_path, str(e)
                    )
                    tmp_cover_path = None
        except Exception as e:
            # Delete .epub file in media/, if `book` is a valid object.
            try:
                if os.path.isfile(book.book_file.path):
                    os.remove(book.book_file.path)
            except:
                pass

            if isinstance(e, ValidationError) and 'already exists' in str(e):
                print ('The book (%s) was not saved because the file already '
                       'exists in the database: %s' % (filename, str(e)))
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
