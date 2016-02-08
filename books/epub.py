# Copyright 2009 One Laptop Per Child
# Author: Sayamindu Dasgupta <sayamindu@laptop.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os.path
import shutil
from sys import version_info
import tempfile
import zipfile

from lxml import etree

import epubinfo


class Epub(object):
    def __init__(self, _file):
        """
        _file: can be either a path to a file (a string) or a file-like object.
        """
        self._file = _file
        self._zobject = None
        self._opfpath = None
        self._ncxpath = None
        self._basepath = None
        self._mimetype = None

        try:
            # Lazy approach to ensure the Epub is really initialized.
            self._tempdir = tempfile.mkdtemp()

            if not self._verify():
                print 'Warning: This does not seem to be a valid ePub file'

            self._get_opf()
            self._get_ncx()

            opffile = self._zobject.open(self._opfpath)
            self._info = epubinfo.EpubInfo(opffile)
        except Exception as e:
            self.close()
            raise e

    def _unzip_file(self, name):
        # Use safe version (2.7+) if possible, that escapes dangerous names.
        if version_info >= (2, 7, 4):
            self._zobject.extract(name, path=self._tempdir)
            return

        # TODO: further restrict the "safe" names (several slashes, relative
        # paths, ...)
        orig_cwd = os.getcwd()
        try:
            os.chdir(self._tempdir)
            # Some weird zip file entries start with a slash, and we don't
            # want to write to the root directory.
            if name.startswith(os.path.sep):
                name = name[1:]
            if name.endswith(os.path.sep) or name.endswith('\\'):
                os.makedirs(name)
            else:
                self._zobject.extract(name)
        except Exception as e:
            raise e
        finally:
            # Make sure that we return to the original directory.
            os.chdir(orig_cwd)

    def _get_opf(self):
        containerfile = self._zobject.open('META-INF/container.xml')

        tree = etree.parse(containerfile)
        root = tree.getroot()

        rfile = './/{urn:oasis:names:tc:opendocument:xmlns:container}rootfile'
        for element in root.iterfind(rfile):
            if element.get('media-type') == 'application/oebps-package+xml':
                self._opfpath = element.get('full-path')

        if self._opfpath.rpartition('/')[0]:
            self._basepath = self._opfpath.rpartition('/')[0] + '/'
        else:
            self._basepath = ''

        containerfile.close()

    def _get_ncx(self):
        opffile = self._zobject.open(self._opfpath)

        tree = etree.parse(opffile)
        root = tree.getroot()

        spine = root.find('.//{http://www.idpf.org/2007/opf}spine')
        tocid = spine.get('toc')

        for element in root.iterfind('.//{http://www.idpf.org/2007/opf}item'):
            if element.get('id') == tocid:
                self._ncxpath = self._basepath + element.get('href')

        opffile.close()

    def _verify(self):
        """
        Method to crudely check to verify that what we
        are dealing with is a ePub file or not
        """
        if isinstance(self._file, basestring):
            if not os.path.exists(self._file):
                return False

        self._zobject = zipfile.ZipFile(self._file)

        if 'mimetype' not in self._zobject.namelist():
            return False

        mtypefile = self._zobject.open('mimetype')
        self._mimetype = mtypefile.readline()

        # Some files seem to have trailing characters
        if not self._mimetype.startswith('application/epub+zip'):
            return False

        return True

    def get_basedir(self):
        """
        Returns the base directory where the contents of the
        ePub has been unzipped
        """
        return self._tempdir

    def get_info(self):
        """
        Returns a EpubInfo object for the open ePpub file
        """
        return self._info

    def get_cover_image_path(self):
        if self._info.cover_image is not None:
            self._unzip_file(self._basepath + self._info.cover_image)
            return os.path.join(self._tempdir, self._basepath,
                                self._info.cover_image)
        else:
            return None

    def as_model_dict(self):
        """Return a tuple with:
        - the fields used for building a `Book` model, as a dict.
        - the path of the temporary file that contains the cover (or None
        if it could not be found). The file is *not* deleted from disk upon
        close().

        TODO: this method should be moved to other layer in order to decouple
        it from the specific Epub implementation on a future refactoring.
        TODO: move prints to logger.
        """
        info = self.get_info()

        # Copy the cover to a temporary file, as otherwise it would be deleted
        # during self.close().
        cover_image_path = self.get_cover_image_path()
        if cover_image_path:
            suffix = os.path.splitext(cover_image_path)[1]
            ret_cover = tempfile.NamedTemporaryFile(suffix=suffix,
                                                    delete=False)
            ret_cover.close()
            ret_cover_path = os.path.abspath(ret_cover.name)
            shutil.copy2(cover_image_path, ret_cover_path)
        else:
            ret_cover_path = None

        # Add identifier.
        # TODO: .strip('urn:uuid:') needed ?
        identifier = info.identifier['value'] if info.identifier else None

        # Print some info about the info found.
        # TODO: move to logging.
        for name, obj in [('Cover image', ret_cover_path),
                          ('Identifier', identifier),
                          ('Language', info.language)]:
            if obj:
                print '  [o] %s found: %s' % (name, obj)
            else:
                print '  [ ] %s not found' % name

        return ({'a_title': info.title,
                 'a_author': info.creator,
                 'a_summary': info.summary,
                 'a_rights': info.rights,
                 'dc_language': info.language,
                 'dc_publisher': info.publisher,
                 'dc_identifier': identifier,
                 'dc_issued': info.date,
                 'mimetype': self._mimetype
                 },
                ret_cover_path)

    def close(self):
        """
        Cleans up (closes open zip files and deletes uncompressed content of
        ePub.
        Please call this when a file is being closed or during application
        exit.
        """
        if self._zobject:
            self._zobject.close()
        shutil.rmtree(self._tempdir)
