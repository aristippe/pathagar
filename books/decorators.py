# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def login_or_public_browse_required(function=None,
                                    redirect_field_name=REDIRECT_FIELD_NAME,
                                    login_url=None):
    """
    Decorator for views that checks that the user is logged in or if the
    Pathagar setting ALLOW_PUBLIC_BROWSE == True, redirecting to the log-in
    page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: settings.ALLOW_PUBLIC_BROWSE or u.is_authenticated(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def login_or_public_add_book_required(function=None,
                                      redirect_field_name=REDIRECT_FIELD_NAME,
                                      login_url=None):
    """
    Decorator for views that checks that the user is logged in or if the
    Pathagar setting ALLOW_PUBLIC_ADD_BOOKS == True, redirecting to the log-in
    page if necessary.
    """
    def check_perms(user):
        if settings.ALLOW_PUBLIC_ADD_BOOKS:
            return True
        if user.is_authenticated():
            if settings.ALLOW_USER_EDIT or user.is_staff:
                return True
            else:
                raise PermissionDenied
        else:
            return False

    actual_decorator = user_passes_test(
        check_perms,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def staff_or_allow_user_edit(login_url=None):
    """
    Decorator for views that checks that the user is logged in, and if the
    user is staff or if the Pathagar setting ALLOW_USER_EDIT == True.
    The user is redirected to the log-in page if not logged in, and if he
    does not have enough permissions a 403 error is raised.
    """
    def check_perms(user):
        if user.is_authenticated():
            if settings.ALLOW_USER_EDIT or user.is_staff:
                return True
            else:
                raise PermissionDenied
        else:
            return False

    return user_passes_test(check_perms, login_url=login_url)
