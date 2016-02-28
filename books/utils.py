# Utility functions for django-taggit
# https://github.com/alex/django-taggit/blob/develop/docs/custom_tagging.txt

def comma_joiner(tags):
    return ', '.join(t.name for t in tags)


def comma_splitter(tag_string):
    return [t.strip().lower() for t in tag_string.split(',') if t.strip()]


def fix_authors(authors):
    authors = authors.strip().replace(', PhD', '') \
        .replace(' PhD', '') \
        .replace(', Ph.D.', '') \
        .replace(' Ph.D.', '') \
        .replace(', Ph.D', '') \
        .replace(' Ph.D', '') \
        .replace(', MD', '') \
        .replace(' MD', '')
    if ',' in authors:
        if not ', Jr.' in authors:
            authors = [b.strip() + ' ' + a.strip()
                       for a, b in zip(*[iter(authors.split(','))] * 2)]
    return authors
