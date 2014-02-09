import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = None
LANGUAGE_CODE = 'en-US'

SITE_ID = 1
USE_I18N = True
USE_L10N = False
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'jvwrlrbd02l%6ywwj66zv6_v5l&le+pdojl@(29qxo2u3e27y0'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates/'),
)

INSTALLED_APPS = (
    # 'django.contrib.staticfiles',
    'gempa',
)

GOOGLE_API_KEY = 'AIzaSyCIoXv8cpQacS9U0Bo4QiUP45m2eH4tHKU'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

EQ_LATEST_SOURCE = ('LATEST', 'http://inatews.bmkg.go.id/rss/csveqslastest.txt',)
EQ_LATEST60_SOURCE = ('LATEST60', 'http://inatews.bmkg.go.id/rss/csvlast60event.txt',)
# GEMPA_GLOBAL_SOURCE = 'http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_week_age.kml'


EQ_CACHE_KEY = 'eqs'
VIDEOS_CACHE_KEY = 'eqvideos'
