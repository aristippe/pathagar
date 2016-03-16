"""
General settings. Please copy "local_settings.py.sample" to
"local_settings.py" in order to override deployment-specific
variables and tailor them to the environment.

For production, you should use a proper web server to deploy Django,
serve static files, and setup a proper database.
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -- Django settings
# Server settings
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    # django-autocomplete-lite before django.contrib.admin
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third-party apps
    'bootstrap3',
    'formtools',
    'taggit',
    'django_comments',
    'pure_pagination',
    'userena',
    'guardian',
    'easy_thumbnails',
    'precise_bbcode',
    # pathagar apps
    'accounts',
    'books.apps.BooksConfig',
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'userena.middleware.UserenaLocaleMiddleware',
]

ROOT_URLCONF = 'pathagar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pathagar.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Authentication
AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',  # userena
    'guardian.backends.ObjectPermissionBackend',  # guardian
    'django.contrib.auth.backends.ModelBackend',
)

SESSION_INVALIDATION_ON_PASSWORD_CHANGE = False

LOGIN_URL = '/accounts/signin/'
LOGOUT_URL = '/accounts/signout/'

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'UserAttributeSimilarityValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'MinimumLengthValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'CommonPasswordValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'NumericPasswordValidator'),
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media
MEDIA_URL = '/static_media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'static_media')

# Other settings
LOGIN_REDIRECT_URL = '/'

SITE_ID = 1

INTERNAL_IPS = ['127.0.0.1']


# -- Third-party apps settings.
# sendfile
SENDFILE_BACKEND = 'sendfile.backends.development'

# taggit
TAGGIT_CASE_INSENSITIVE = True
TAGGIT_STRING_FROM_TAGS = 'books.utils.comma_joiner'
TAGGIT_TAGS_FROM_STRING = 'books.utils.comma_splitter'

# easy-thumbnails
THUMBNAIL_ALIASES = {
    '': {
        'thumb': {'size': (100, 100), 'crop': False},
    },
}
THUMBNAIL_DEBUG = True

# django-guardian
ANONYMOUS_USER_ID = -1

# django-userena
AUTH_PROFILE_MODULE = 'accounts.Profile'
USERENA_ACTIVATION_DAYS = 10
USERENA_PROFILE_DETAIL_TEMPLATE = 'accounts/profile_detail.html'
USERENA_SIGNIN_REDIRECT_URL = '/accounts/%(username)s/'

# django-pure-pagination
PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 5,
    'MARGIN_PAGES_DISPLAYED': 1,
    'SHOW_FIRST_PAGE_WHEN_INVALID': True,
}


# -- Pathagar settings.
# Number of books shown per page in the OPDS catalogs and in the HTML pages.
BOOKS_PER_PAGE = 50

DEFAULT_BOOK_STATUS = 'Published'

# PK for Status(status=='Published')
BOOK_PUBLISHED = 1

# Allow non logged in users to upload books
ALLOW_PUBLIC_ADD_BOOKS = False

# Allow non logged in users to browse the site
ALLOW_PUBLIC_BROWSE = False

# Allow regular users to modify Books and Authors.
ALLOW_USER_EDIT = False

ALLOW_USER_COMMENTS = True


# -- Local settings.
# Deployment-specific variables are imported from local_settings.py
try:
    from local_settings import *  # NOQA
except ImportError:
    pass
