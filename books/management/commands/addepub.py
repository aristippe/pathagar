from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.db.utils import IntegrityError

import os

from books.models import Language, Book, Status
from books.epub import Epub
from books.langlist import langs

import sys


def get_epubs(path):
    """Returns a list of EPUB(s)"""
    epub_list = []

    # for root, dirs, files in os.walk(path):
    #     print 'Importing %s.' % files
    #     for name in files:
    #         if name.lower().endswith('.epub'):
    #             epub_list.append(os.path.join(root, name))
    # return epub_list

    for root, dirs, files in os.walk(path):
        for name in files:
            if name.lower().endswith('.epub'):
                epub_list.append(os.path.join(root, name))
    return epub_list


class Command(BaseCommand):
    help = "Adds a book collection (via a directory containing EPUB file(s))"
    args = 'Absolute path to directory of EPUB files'

    def handle(self, dirpath='', *args, **options):
        if not os.path.exists(dirpath):
            raise CommandError("%r is not a valid path" % dirpath)

        if os.path.isdir(dirpath):
            names = get_epubs(dirpath)
            for name in names:
                # TODO call self.process_epub
                # self.process_epub(name)

                print '\nImporting %s' % name
                if Book.objects.filter(book_file=name).exists():
                    print "- already imported"
                else:
                    info = None
                    try:
                        e = Epub(name)
                        info = e.get_info()
                    except:
                        print "- error: not a valid epub file."  # % name
                        continue

                    lang = Language.objects.filter(code=info.language)
                    # exists in table
                    if lang:
                        lang = lang[0]
                    else:
                        # does not exist in table, if not null, add to table
                        if info.language is None:
                            lang = None
                        else:
                            if len(info.language) <= 5:
                                lang = Language()
                                lang.add(info.language)
                            lang = None

                    # XXX: Hacks below
                    if not info.title:
                        info.title = ''
                    if not info.summary:
                        info.summary = ''
                    if not info.creator:
                        info.creator = ''
                    if not info.rights:
                        info.rights = ''

                    f = open(name)
                    pub_status = Status.objects.get(status='Published')
                    if info.identifier is not None:
                        identifier = info.identifier['value']  # .strip('urn:uuid:')
                    else:
                        identifier = None
                    book = Book(book_file=File(f),
                                a_title=info.title,
                                a_author=info.creator,
                                a_summary=info.summary,
                                a_rights=info.rights,
                                dc_language=lang,
                                dc_publisher=info.publisher,
                                dc_identifier=identifier,
                                dc_issued=info.date,
                                a_status=pub_status)

                    try:
                        book.save()
                    # FIXME: Find a better way to do this.
                    except IntegrityError as e:
                        if str(e) == "column file_sha256sum is not unique":
                            print "The book (", book.book_file, ") was not saved because the file already exists in the database."
                        else:
                            # raise CommandError('Error adding file %s: %s' % (book.book_file, sys.exc_info()[1]))
                            print 'Error adding file %s: %s' % (book.book_file, sys.exc_info()[1])
                    except:
                        # raise CommandError('Error adding file %s: %s' % (book.book_file, sys.exc_info()[1]))
                        print 'Error adding file %s: %s' % (book.book_file, sys.exc_info()[1])

        if os.path.isfile(dirpath):
            self.process_epub(dirpath)

    @staticmethod
    def process_epub(name):
        print '\nImporting %s' % name
        if Book.objects.filter(book_file=name).exists():
            print "- already imported"
        else:
            info = None
            try:
                e = Epub(name)
                info = e.get_info()
            except:
                print "%s is not a valid epub file" % name
            lang = Language.objects.filter(code=info.language)
            # exists in table
            if lang:
                lang = lang[0]
            else:
                # does not exist in table, if not null, add to table
                if info.language is None:
                    lang = None
                else:
                    if len(info.language) <= 5:
                        lang = Language()
                        lang.add(info.language)
                    lang = None

            # XXX: Hacks below
            if not info.title:
                info.title = ''
            if not info.summary:
                info.summary = ''
            if not info.creator:
                info.creator = ''
            if not info.rights:
                info.rights = ''

            f = open(name)
            pub_status = Status.objects.get(status='Published')
            if info.identifier is not None:
                print "Identifier: %s" % info.identifier['value']
                identifier = info.identifier['value']  # .strip('urn:uuid:') # needed ?
            else:
                identifier = None
            book = Book(book_file=File(f),
                        a_title=info.title,
                        a_author=info.creator,
                        a_summary=info.summary,
                        a_rights=info.rights,
                        dc_language=lang,
                        dc_publisher=info.publisher,
                        dc_identifier=identifier,
                        dc_issued=info.date,
                        a_status=pub_status)

            try:
                book.save()
            # FIXME: Find a better way to do this.
            except IntegrityError as e:
                if str(e) == "column file_sha256sum is not unique":
                    print "The book (", book.book_file, ") was not saved because the file already exists in the database."
                else:
                    # raise CommandError('Error adding file %s: %s' % (book.book_file, sys.exc_info()[1]))
                    print '  - error: %s' % sys.exc_info()[1]
            except:
                # raise CommandError('Error - %s' % (book.book_file, sys.exc_info()[1]))
                print '  - error: %s' % (sys.exc_info()[1])
