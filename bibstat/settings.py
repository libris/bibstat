"""
Django settings for bibstat project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
from pathlib import Path
#from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

#reload(sys)
#sys.setdefaultencoding('utf-8')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

"""
----------------------------------------------------------
Environment specific settings, hostnames, usernames e t c
----------------------------------------------------------
"""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False
BLOCK_SURVEY = False
BLOCK_REPORTS = False
ANALYTICS_ENABLED = False

ALLOWED_HOSTS = [
    ".bibstat-stg.kb.se",
    ".bibstat-stg.libris.kb.se"
]

BIBSTAT_BLOG_BASE_URL = "https://www.kb.se/biblioteksstatistik"

# Email details
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_SENDER = 'biblioteksstatistik@kb.se'

LOG_LEVEL = 'WARNING'

# Override above with local settings if present
try:
    from .settings_local import *
except ImportError as e:
    print(f"local settings could not be imported: {e}")

"""
-----------------------------------------------------------
"""

# Application definition
INSTALLED_APPS = [
    # Django standard apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_js_reverse',

    # Bibstat specific apps
    #'mongoengine.django.mongo_auth',
    'django_mongoengine',
    'django_mongoengine.mongo_auth',
    #'django_mongoengine.mongo_admin',
    'libstat'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bibstat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

SESSION_ENGINE = 'django_mongoengine.sessions'
SESSION_SERIALIZER = 'django_mongoengine.sessions.BSONSerializer'

WSGI_APPLICATION = 'bibstat.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    # Configuring Django ORM with dummy DB since MongoEngine config does not use this setting
    'default': {
        'ENGINE': ''
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

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

LOGIN_REDIRECT_URL = '/surveys'

"""
    Logging
"""
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        # 'file': {
        #             'level': 'DEBUG',
        #             'class': 'logging.FileHandler',
        #             'filename': 'logs/bibstat.log',
        #             'formatter': 'verbose'
        #             },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'libstat': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    }
}
if DEBUG:
    # make all loggers use the console.
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['console']

"""
    MongoEngine settings
"""

# Enable some basic auth features such as get_user(). Define a custom user model if advanced auth features are required
AUTHENTICATION_BACKENDS = ('django_mongoengine.mongo_auth.backends.MongoEngineBackend',)
AUTH_USER_MODEL = 'mongo_auth.MongoUser'
#MONGOENGINE_USER_DOCUMENT = 'mongoengine.django.auth.User'

# Store Django sessions in MongoDB backend
SESSION_ENGINE = 'django_mongoengine.sessions'
#SESSION_SERIALIZER = 'mongoengine.django.sessions.BSONSerializer'
#SESSION_COOKIE_AGE = 2592000

# Initialize MongoDB connection
#MONGODB_DATABASE_HOST = 'mongodb://%s:%s@%s/%s' % (MONGODB_USER, MONGODB_PASSWD, MONGODB_HOST, MONGODB_NAME)

#mongoengine.connect(MONGODB_NAME, host=MONGODB_DATABASE_HOST)
# mongoengine.connect(MONGODB_NAME)

# Use custom test runner to skip setup/teardown of fixtures for test database
TEST_RUNNER = 'libstat.tests.MongoEngineTestRunner'
