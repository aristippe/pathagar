from collections import namedtuple

from language_tags import tags
from pycountry import languages

LanguageTuple = namedtuple('languagetuple', ['code', 'description'])
# ISO-6639/2 bibliographic synonyms.
# https://en.wikipedia.org/wiki/ISO_639-2#B_and_T_codes
ISO_6639_2_B = {'alb': 'sqi',
                'arm': 'hye',
                'baq': 'eus',
                'tib': 'bod',
                'bur': 'mya',
                'cze': 'ces',
                'chi': 'zho',
                'wel': 'cym',
                'ger': 'deu',
                'dut': 'nld',
                'per': 'fas',
                'fre': 'fra',
                'geo': 'kat',
                'gre': 'ell',
                'ice': 'isl',
                'mac': 'mkd',
                'mao': 'mri',
                'may': 'msa',
                'rum': 'rom',
                'slo': 'slk',
                }


# Utility functions for django-taggit
# https://github.com/alex/django-taggit/blob/develop/docs/custom_tagging.txt
def comma_joiner(tags):
    return ', '.join(t.name for t in tags)


def comma_splitter(tag_string):
    return [t.strip().lower() for t in tag_string.split(',') if t.strip()]


def fix_authors(authors):
    authors = authors.strip().replace(', PhD', '') \
        .replace(' PhD', '') \
        .replace(', PH.D.', '') \
        .replace(' PH.D.', '') \
        .replace(', Ph.D.', '') \
        .replace(' Ph.D.', '') \
        .replace(', Ph.D', '') \
        .replace(' Ph.D', '') \
        .replace(', M.D.', '') \
        .replace(' M.D.', '') \
        .replace(', MD', '') \
        .replace(' MD', '')
    if ',' in authors:
        if ', Jr.' not in authors:
            authors = [b.strip() + ' ' + a.strip()
                       for a, b in zip(*[iter(authors.split(','))] * 2)]
    return authors


def standardize_language(code):
    """Match `code` to a standard RFC5646 or RFC3066 language. The following
    approaches are tried in order:
    * Match a RFC5646 language string.
    * Match a RFC3066 language string.
    * Use a ISO-6639/2 bibliographic synonym, and match a RFC3066 language
    string for the ISO-6639/2 terminological code.
    If no results are found, `None` is returned.

    http://www.idpf.org/epub/30/spec/epub30-publications.html#sec-opf-dclanguage
    http://www.idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.12

    :param code: string with a language code ('en-GB', ...)
    :returns: `LanguageTuple` with the RFC5646 code and the list of description
    tags, or `None` if the language could not be identified.
    """
    if not code:
        return None

    # Try RFC5646 (for EPUB 3).
    if tags.check(code):
        return LanguageTuple(code=code.lower(),
                             description=tags.description(code))

    # Try RFC3066 (for EPUB 2).
    # Try to get the ISO639-1 code for the language.
    try:
        lang = languages.get(iso639_2T_code=code)
        new_code = lang.iso639_1_code
    except KeyError:
        # Try synonym.
        if code in ISO_6639_2_B.keys():
            try:
                lang = languages.get(iso639_2T_code=ISO_6639_2_B[code])
                new_code = lang.iso639_1_code
            except KeyError:
                return None
        else:
            return None

    # Try RFC5646 for the ISO639-1 code.
    if tags.check(new_code):
        return LanguageTuple(code=new_code.lower(),
                             description=tags.description(new_code))
    return None
