# encoding: UTF-8


"""
Django settings for cfgmgmtcenter project.
"""

from os import path
import ldap
import logging
from django_auth_ldap.config import LDAPSearch, ActiveDirectoryGroupType


PROJECT_ROOT = path.dirname(path.abspath(path.dirname(__file__)))
BASE_DIR = path.dirname(path.abspath(path.dirname(__file__)))

DEBUG = True

LOGIN_URL = "/login/"

ALLOWED_HOSTS = (
    '*',
)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.mysql',
        # Or path to database file if using sqlite3.
        'NAME': 'cfgmgmtcenter',
        # Not used with sqlite3.
        'USER': 'djangoadmin',
        # Not used with sqlite3.
        'PASSWORD': 'abcd@123',
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': '127.0.0.1',
        # Set to empty string for default. Not used with sqlite3.
        'PORT': '3306',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-Hans'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = path.join(PROJECT_ROOT, 'static').replace('\\', '/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'n(bd1f1c%e8=_xad02x5qtfn%wgwpi492e$8_erx+d)!tpeoim'


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'pagination_bootstrap.middleware.PaginationMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'cfgmgmtcenter.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'cfgmgmtcenter.wsgi.application'


INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'debug_toolbar',
    'django_select2',
    'rest_framework',
    'rest_framework.authtoken',
    'django_extensions',
    'simple_history',
    'guardian',
    'pagination_bootstrap',
    'djcelery',
    'webui',
    'api',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Specify the default test runner.
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Templates setting from 1.8
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                'django.core.context_processors.request',
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# REST Framework, Enable Filter, Pagination
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# Django Auth Ldap
logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

AUTH_LDAP_SERVER_URI = "ldap://ymt-ad-01.ymt.corp"
AUTH_LDAP_BIND_DN = "CN=gitlabserviceaccount,OU=IT运维,OU=集团产品研发,OU=ymatou,DC=ymt,DC=corp"
AUTH_LDAP_BIND_PASSWORD = "ymt@123"
AUTH_LDAP_USER_SEARCH = LDAPSearch("OU=ymatou, DC=ymt, DC=corp", ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")

AUTH_LDAP_USER_ATTR_MAP = {
       "first_name": "givenName",
       "last_name": "sn",
}

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

# django-guardian
ANONYMOUS_USER_ID = -1

# Select 2
AUTO_RENDER_SELECT2_STATICS = True
SELECT2_BOOTSTRAP = True

# cfgmgmtcenter Setting
KNOWN_DEPRATMENTS = {
    u'it运维':'ops',
    u'研发-m2c':'m2c',
    u'研发-c2c':'c2c',
    u'研发-xlobo':'xlobo',
    u'架构':'infra',
    u'测试':'test',
}

PROD_ENV_NAME = 'STAGING_PROD'

# gitlab configuration
GITLAB_SERVER = "http://gitlab.ops.ymt.corp"
GITLAB_ACCOUNT_TOKEN ="Dk4tWyy48ffdfhErsUxN"
GITLAB_USERNAME = 'root'
GITLAB_PASSWORD = 'ymt%401234'

# ftp configuration
PACKAGE_TEMP_PATH = path.join(PROJECT_ROOT, 'tmp')
FTP_PROD_SERVER = '172.16.100.81'
FTP_PROD_USERNAME = 'config'
FTP_PROD_PASSWORD = 'config'

FTP_TEST_SERVER = '172.16.100.81'
FTP_TEST_USERNAME = 'testconfig'
FTP_TEST_PASSWORD = 'Welcome123'

# cryptography key
FERNET_KEYS = ['sU51foKs7IHVgxhTCLQDQed4t7cox54ObbUEYuPXceY=']

# Debug Toolbar
DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': '//apps.bdimg.com/libs/jquery/2.1.4/jquery.min.js',
}

# Celery Settings
BROKER_URL = 'redis://:ce645e80fedd0d5e6b264b3e424bffe0@127.0.0.1:6379/1'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'

# We have to enable this setting since we have low-traffic workers.
# http://docs.celeryproject.org/en/latest/configuration.html#short-lived-sessions
CELERY_RESULT_DB_SHORT_LIVED_SESSIONS = True

