"""
This settings are for testing Pathagar with the Django development
server.  It will use a SQLite database in the current directory and
Pathagar will be available at http://127.0.0.1:8000 loopback address.

For production, you should use a proper web server to deploy Django,
serve static files, and setup a proper database.

"""

import os

# Server settings:

SERVER_NAME = 'Pathagar'

# Books settings:

BOOKS_PER_PAGE = 50  # Number of books shown per page in the OPDS
# catalogs and in the HTML pages.

BOOKS_STATICS_VIA_DJANGO = True
DEFAULT_BOOK_STATUS = 'Published'

# Allow non logged in users to upload books
ALLOW_PUBLIC_ADD_BOOKS = False

# sendfile settings:

SENDFILE_BACKEND = 'sendfile.backends.development'

# Get current directory to get media and templates while developing:
CUR_DIR = os.path.dirname(__file__)

TIME_ZONE = 'America/Los_Angeles'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

MEDIA_ROOT = os.path.join(CUR_DIR, 'static_media')

MEDIA_URL = '/static_media/'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'pathagar.urls'

INTERNAL_IPS = ('127.0.0.1',)

TEMPLATE_DIRS = (
    os.path.join(CUR_DIR, 'templates'),
)

STATIC_ROOT = os.path.join(CUR_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(CUR_DIR, 'static'),
)

ALLOW_USER_COMMENTS = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.formtools',
    'tagging',  # TODO old
    'taggit',
    'django.contrib.comments',
    'pathagar.books'
)

LOGIN_REDIRECT_URL = '/'

# Deployment-specific variables are imported from local_settings.py
try:
    from local_settings import *
except ImportError:
    pass
