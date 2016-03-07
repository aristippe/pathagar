from django import template

register = template.Library()


def field_width(field_name):
    """Returns the field size for the bootstrap_field template tag.
    """
    if field_name in ['dc_issued', 'a_status', 'downloads']:
        return 'col-md-3'
    elif field_name in ['dc_language']:
        return 'col-md-6'
    else:
        return 'col-md-10'

register.filter('field_width', field_width)
