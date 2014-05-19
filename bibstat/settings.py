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

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3x%=t4cm@eszqbwuw@00f**ol@8^kqomtm8-%x&5_ydq9rm(nl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    # Django standard apps
    'django.contrib.admin', # TODO: Remove?
    'django.contrib.auth',  # TODO: Remove?
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Bibstat specific apps
    'mongoengine.django.mongo_auth',
    'mongonaut',
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

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

#
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

# Initialize MongoDB connection
_MONGODB_USER = 'bibstat'
_MONGODB_PASSWD = 'bibstat'
_MONGODB_HOST = 'localhost'
_MONGODB_NAME = 'bibstat'
_MONGODB_DATABASE_HOST = \
    'mongodb://%s:%s@%s/%s' \
    % (_MONGODB_USER, _MONGODB_PASSWD, _MONGODB_HOST, _MONGODB_NAME)

#mongoengine.connect(_MONGODB_NAME, host=_MONGODB_DATABASE_HOST)
mongoengine.connect(_MONGODB_NAME)

# Mongonaut Admin GUI static files
MONGONAUT_JQUERY = "/static/js/plugins/jquery/1.7.1/jquery.min.js"
MONGONAUT_TWITTER_BOOTSTRAP = "/static/js/plugins/bootstrap/css/bootstrap.css"
MONGONAUT_TWITTER_BOOTSTRAP_ALERT = "/static/js/plugins/bootstrap/js/bootstrap.js"

