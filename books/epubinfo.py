# Copyright (C) 2010, One Laptop Per Child
# Copyright (C) 2010, Kushal Das
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

from lxml import etree


class EpubInfo():  # TODO: Cover the entire DC range
    def __init__(self, opffile):
        self._tree = etree.parse(opffile)
        self._root = self._tree.getroot()
        self._e_metadata = self._root.find('{http://www.idpf.org/2007/opf}metadata')

        self.title = self._get_title()
        self.creator = self._get_creator()
        self.date = self._get_date()
        self.subject = self._get_subject()
        self.source = self._get_source()
        self.rights = self._get_rights()
        self.identifier = self._get_identifier()
        self.language = self._get_language()
        self.publisher = self._get_publisher()
        self.summary = self._get_description()
        self.cover_image = self._get_cover_image()

    def _get_data(self, tagname):
        element = self._e_metadata.find(tagname)
        return element.text

    def _get_description(self):
        try:
            ret = self._get_data('.//{http://purl.org/dc/elements/1.1/}description')
        except AttributeError:
            return None

        return ret

    def _get_title(self):
        try:
            ret = self._get_data('.//{http://purl.org/dc/elements/1.1/}title')
        except AttributeError:
            return None

        return ret

    def _get_creator(self):
        try:
            ret = self._get_data('.//{http://purl.org/dc/elements/1.1/}creator')
        except AttributeError:
            return None
        return ret

    def _get_date(self):
        # TODO: iter
        try:
            ret = self._get_data('.//{http://purl.org/dc/elements/1.1/}date')
        except AttributeError:
            return None

        return ret

    def _get_source(self):
        try:
            ret = self._get_data('.//{http://purl.org/dc/elements/1.1/}source')
        except AttributeError:
            return None

        return ret

    def _get_rights(self):
        try:
            ret = self._get_data('.//{http://purl.org/dc/elements/1.1/}rights')
        except AttributeError:
            return None

        return ret

    def _get_identifier(self):
        # TODO: iter
        element = self._e_metadata.find('.//{http://purl.org/dc/elements/1.1/}identifier')

        if element is not None:
            return {'id':element.get('id'), 'value':element.text}
        else:
            return None

    def _get_language(self):
        # print "Language: % " % self._get_data('.//{http://purl.org/dc/elements/1.1/}language')
        try:
            ret = self._get_data('.//{http://purl.org/dc/elements/1.1/}language')
        except AttributeError:
            return None

        return ret

    def _get_publisher(self):
        # print "Publisher: %" % self._get_data('.//{http://purl.org/dc/elements/1.1/}creator')
        try:
            ret = self._get_data('.//{http://purl.org/dc/elements/1.1/}publisher')
        except AttributeError:
            return None
        return ret

    def _get_subject(self):
        try:
            subjectlist = []
            for element in self._e_metadata.iterfind('.//{http://purl.org/dc/elements/1.1/}subject'):
                subjectlist.append(element.text)
        except AttributeError:
            return None

        return subjectlist

    def _get_cover_image(self):
        # TODO check if cover is image
        meta_content_cover = None
        for element in self._e_metadata.iterfind('{http://www.idpf.org/2007/opf}meta'):
            if element.get('name') == 'cover':
                meta_content_cover = element.get('content')

        if meta_content_cover:
            for node in self._tree.iter():
                if node.tag == '{http://www.idpf.org/2007/opf}item':
                    if node.attrib['id'] == meta_content_cover:
                        cover = node.attrib['href']
            return cover
        else:
            return None
