"""
Django settings for bibstat project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

"""
----------------------------------------------------------
Environment specific settings, hostnames, usernames e t c
----------------------------------------------------------
"""
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3x%=t4cm@eszqbwuw@00f**ol@8^kqomtm8-%x&5_ydq9rm(nl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = [
    ".bibstat-stg.libris.kb.se",
    ".bibstat-stg.libris.kb.se.",
]

# Base url for api, i.e. http://stats.kb.se
API_BASE_URL = "http://bibstat-stg.libris.kb.se/statistics"
BIBDB_BASE_URL = "http://bibdbclone.libris.kb.se"

# DB connection details
MONGODB_HOST = 'localhost'
MONGODB_NAME = 'bibstat'
MONGODB_USER = 'bibstat'
MONGODB_PASSWD = 'bibstat'

# Override above with local settings if present
try:
    from settings_local import *
except ImportError:
    print "local settings could not be imported"

"""
-----------------------------------------------------------
"""

# Application definition
INSTALLED_APPS = (
    # Django standard apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Bibstat specific apps
    'mongoengine.django.mongo_auth',
    'libstat'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'bibstat.urls'

WSGI_APPLICATION = 'bibstat.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    # Configuring Django ORM with dummy DB since MongoEngine config does not use this setting
    'default': {
        'ENGINE': 'django.db.backends.dummy'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'sv-se'

TIME_ZONE = 'Europe/Stockholm'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'

# Common static resources not tied to any application.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
    # TODO '/var/www/static/',
)

LOGIN_REDIRECT_URL = 'libstat.views.index'

# MongoEngine settings
#
import mongoengine

# Enable some basic auth features such as get_user(). Define a custom user model if advanced auth features are required
AUTHENTICATION_BACKENDS = (
    'mongoengine.django.auth.MongoEngineBackend',
)
AUTH_USER_MODEL = 'mongo_auth.MongoUser'
MONGOENGINE_USER_DOCUMENT = 'mongoengine.django.auth.User'

# Store Django sessions in MongoDB backend
SESSION_ENGINE = 'mongoengine.django.sessions'
SESSION_SERIALIZER = 'mongoengine.django.sessions.BSONSerializer'
# 1h session timeout, cleanup of sessions is done with document TTL in mongodb
SESSION_COOKIE_AGE = 60*60*1   

# Initialize MongoDB connection
MONGODB_DATABASE_HOST = 'mongodb://%s:%s@%s/%s' % (MONGODB_USER, MONGODB_PASSWD, MONGODB_HOST, MONGODB_NAME)

#mongoengine.connect(MONGODB_NAME, host=MONGODB_DATABASE_HOST)
mongoengine.connect(MONGODB_NAME)

# Use custom test runner to skip setup/teardown of fixtures for test database
TEST_RUNNER = 'libstat.tests.MongoEngineTestRunner'
