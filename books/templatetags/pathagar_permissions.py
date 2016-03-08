from django import template
from django.conf import settings


register = template.Library()


def can_upload(user):
    """Returns True if the user has upload permissions, taking into account
    Pathagar settings and the User.

    TODO: if we switch to a Django group/permission system, this is probably
    better done directly checking permissions.
    """
    if settings.ALLOW_PUBLIC_ADD_BOOKS:
        return True
    if user.is_authenticated():
        if settings.ALLOW_USER_EDIT or user.is_staff:
            return True
    return False


register.filter('can_upload', can_upload)
