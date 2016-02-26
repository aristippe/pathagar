# Utility functions for django-taggit
# https://github.com/alex/django-taggit/blob/develop/docs/custom_tagging.txt

def comma_joiner(tags):
    return ', '.join(t.name for t in tags)

def comma_splitter(tag_string):
    return [t.strip().lower() for t in tag_string.split(',') if t.strip()]
