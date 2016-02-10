"""Helper for dealing with the sample epubs stored on resources.
"""
import os
from collections import namedtuple

from django.conf import settings

RSRC_DIR = os.path.abspath(os.path.join(settings.CUR_DIR,
                                        '../resources/epubsamples'))
SampleEpub = namedtuple('SampleEpub', ('key', 'filename', 'fullpath',
                                       'is_valid', 'has_cover'))

# List of sample epubs, with their interesting properties.
# TODO: the 'fullpath' property is a bit messy at the moment, should be
# calculated automatically based on 'filename'.
EPUBS_ALL = [SampleEpub('epub30-spec', 'epub30-spec.epub',
                        os.path.join(RSRC_DIR, 'epub30-spec.epub'),
                        True, False),
             SampleEpub('figure-gallery', 'figure-gallery-bindings.epub',
                        os.path.join(RSRC_DIR, 'figure-gallery-bindings.epub'),
                        True, True),
             SampleEpub('not-epub', 'not-an-epub.epub',
                        os.path.join(RSRC_DIR, 'not-an-epub.epub'),
                        False, False),
             SampleEpub('not-epub-zip', 'not-an-epub-but-a-zip.epub',
                        os.path.join(RSRC_DIR, 'not-an-epub-but-a-zip.epub'),
                        False, False)]

# Convenience lists of epub, using 'key' as the identifier.
EPUBS_VALID = [epub for epub in EPUBS_ALL if epub.is_valid]
EPUBS_NOT_VALID = [epub for epub in EPUBS_ALL if not epub.is_valid]
EPUBS_COVER = [epub for epub in EPUBS_ALL if epub.has_cover]
EPUBS_NOT_COVER = [epub for epub in EPUBS_ALL if not epub.has_cover]
