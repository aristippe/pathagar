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

import logging
import os.path
import shutil
import tempfile
import zipfile
from sys import version_info

import lxml.html
from lxml import etree

import epubinfo


class Epub(object):
    def __init__(self, _file):
        """
        _file: can be either a path to a file (a string) or a file-like object.
        """
        self._file = _file
        self._zobject = None
        self._opf_path = None
        self._ncx_path = None
        self._base_path = None
        self._mimetype = None

        try:
            # Lazy approach to ensure the Epub is really initialized.
            self._tempdir = tempfile.mkdtemp()

            if not self._verify():
                print 'Warning: This does not seem to be a valid ePub file'

            self._get_opf()
            self._get_ncx()

            opf_file = self._zobject.open(self._opf_path)
            self._info = epubinfo.EpubInfo(opf_file)
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
        container_file = self._zobject.open('META-INF/container.xml')

        tree = etree.parse(container_file)
        root = tree.getroot()

        rfile = './/{urn:oasis:names:tc:opendocument:xmlns:container}rootfile'
        for element in root.iterfind(rfile):
            if element.get('media-type') == 'application/oebps-package+xml':
                self._opf_path = element.get('full-path')

        if self._opf_path.rpartition('/')[0]:
            self._base_path = self._opf_path.rpartition('/')[0] + '/'
        else:
            self._base_path = ''

        container_file.close()

    def _get_ncx(self):
        opffile = self._zobject.open(self._opf_path)

        tree = etree.parse(opffile)
        root = tree.getroot()

        spine = root.find('.//{http://www.idpf.org/2007/opf}spine')
        tocid = spine.get('toc')

        for element in root.iterfind('.//{http://www.idpf.org/2007/opf}item'):
            if element.get('id') == tocid:
                self._ncx_path = self._base_path + element.get('href')

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
        Returns a EpubInfo object for the open ePub file
        """
        return self._info

    def get_cover_image_path(self):
        """
        Epubinfo returns cover_image as either an image or xhtml. If xhtml,
        parse to find image
        """
        if not self._info.cover_image:
            return None

        cover_image = os.path.join(self._tempdir,
                                   self._base_path,
                                   self._info.cover_image)

        try:
            self._unzip_file(self._base_path + self._info.cover_image)
            if self._info.cover_image.lower().endswith(('.bmp',
                                                        '.gif',
                                                        '.jpg',
                                                        '.jpeg',
                                                        '.png')):
                return cover_image
        except Exception as e:
            logging.exception(e)
            return None

        # Begin XHTML handling
        parent = lxml.html.parse(cover_image)

        # img tag
        images = parent.xpath('//img/@src')
        if images:
            img = images[0]
            image_base_path = os.path.dirname(self._info.cover_image)
            image_path = os.path.normpath(image_base_path + '/' + img)

            # In case of leading or trailing slash
            joined_path = (self._base_path + image_path).replace('//', '/')
            try:
                self._unzip_file(joined_path)
                return os.path.join(self._tempdir, joined_path)
            except Exception as e:
                logging.exception(e)
                return None

        # SVG image
        svg_image = parent.xpath('//image')
        if svg_image:
            image_path = os.path.normpath(
                self._base_path +
                os.path.dirname(self._info.cover_image) + '/' +
                svg_image[0].attrib['xlink:href']
            )
            try:
                self._unzip_file(image_path)
                return os.path.join(self._tempdir, image_path)
            except Exception as e:
                logging.exception(e)
                return None

        # https://stackoverflow.com/questions/2932408
        # TODO cover as svg string
        # SVG String - cairosvg requires Python 3.4+, untested
        # svg = parent.xpath('//svg')
        # if svg:
        #     logging.warning(svg[0])
        #     image_path = open(os.path.join(self._tempdir + cover.png'),'w')
        #     cairosvg.svg2png(bytestring=svg,write_to=fout)
        #     image_path.close()
        #     # return image_path

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
                          ('Authors', info.creators),
                          ('Language', info.language)]:
            if obj:
                print '  [o] %s found: %s' % (name, obj)
            else:
                print '  [ ] %s not found' % name

        return ({'a_title': info.title,
                 'a_summary': info.summary,
                 'a_rights': info.rights,
                 'dc_language': info.language,
                 'dc_identifier': identifier,
                 'dc_issued': info.date,
                 'mimetype': self._mimetype
                 },
                info.creators, info.publishers, ret_cover_path, info.subjects)

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
