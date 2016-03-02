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
