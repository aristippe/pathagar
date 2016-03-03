# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


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
    actual_decorator = user_passes_test(
        lambda u: settings.ALLOW_PUBLIC_ADD_BOOKS or u.is_authenticated(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
