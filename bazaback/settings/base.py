"""
Django settings for bazaback project.

Generated by 'django-admin startproject' using Django 2.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from django.core.exceptions import ImproperlyConfigured

from celery.schedules import crontab


def get_env_var(name):
    try:
        return os.environ[name]
    except KeyError:
        raise ImproperlyConfigured(
            'Set the environment variable %s' % name
        )


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_var('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels'
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'oauth2_provider',
    'simple_history',
    'versatileimagefield',
    'mjml'
]

BAZA_APPS = [
    'userprofile',
    'mockapi',
    'proxcdb',
    'notifications',
    'authclient',
    'stripepayment',
    'donation',
    'coinpurchase',
    'bazasignup',
    'landingcontact',
    'taigaissuecreator',
    'publicusers',
    'messenger',
    'group',
    'grouppost',
    'paypalpayment',
    'coinbasepay',
    'hashtag'
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + BAZA_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bazaback.urls'

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

WSGI_APPLICATION = 'bazaback.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'staticfiles')]

# Media files

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Fixture dirs

FIXTURE_DIRS = [os.path.join(BASE_DIR, 'fixtures')]

# GEOIP files
GEOIP_PATH = os.path.join(BASE_DIR, 'geoip')


# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    )
}


# CELERY
CELERY_BROKER_URL = 'redis://' + get_env_var('REDIS_HOST') + ':6379/0'
CELERY_RESULT_BACKEND = 'redis://' + get_env_var('REDIS_HOST') + ':6379/0'
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULE = {
    'process_flagged_for_delete_group': {
        'task': 'group.tasks.task_process_flagged_for_delete_group',
        'schedule': crontab(minute=0, hour=12)
    }
}

# Channels ASGI application
ASGI_APPLICATION = 'bazaback.routing.application'


# Email verification
# Can be one of these 'none', 'mandatory', 'optional'
EMAIL_VERIFICATION = 'mandatory'


# Site type
SITE_TYPE = get_env_var('SITE_TYPE')


# Host URL
HOST_URL = get_env_var('HOST')

# Auth email address
INITIATOR_EMAIL = get_env_var('INITIATOR_EMAIL')

# Auth introspect
CENTRAL_AUTH_INTROSPECT_URL = get_env_var('CENTRAL_AUTH_INTROSPECT_URL')
CENTRAL_AUTH_INTROSPECT_CLIENT_ID = get_env_var(
    'CENTRAL_AUTH_INTROSPECT_CLIENT_ID')
CENTRAL_AUTH_INTROSPECT_CLIENT_SECRET = get_env_var(
    'CENTRAL_AUTH_INTROSPECT_CLIENT_SECRET')
CENTRAL_AUTH_USER_LOGIN_CLIENT_ID = get_env_var(
    'CENTRAL_AUTH_USER_LOGIN_CLIENT_ID'
)
CENTRAL_AUTH_USER_LOGIN_CLIENT_SECRET = get_env_var(
    'CENTRAL_AUTH_USER_LOGIN_CLIENT_SECRET'
)


# OAUTH2 Provider
# TODO: Resource server token expires,
# check dot source if they provide method to refresh,
# Otherwise implement own
OAUTH2_PROVIDER = {
    'RESOURCE_SERVER_INTROSPECTION_URL': '%s://%s/o/introspect/' % (
        'http' if SITE_TYPE == 'local' else 'https',
        CENTRAL_AUTH_INTROSPECT_URL,
    ),
    'RESOURCE_SERVER_AUTH_TOKEN': get_env_var('RESOURCE_SERVER_AUTH_TOKEN'),
}


# DJANGO Cache
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': get_env_var('REDIS_HOST') + ':6379',
    },
}


# CHANNEL
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(get_env_var('REDIS_HOST'), 6379)],
        },
    },
}


# Registration settings
REGISTRATION_ENABLED = bool(get_env_var('REGISTRATION_ENABLED'))


# Stripe
STRIPE_SECRET_KEY = get_env_var('STRIPE_SECRET_KEY')

# EMAIL_SERVER
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = get_env_var('DJANGO_EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_HOST_USER = get_env_var('DJANGO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_var('DJANGO_EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True

# TWILIO
TWILIO_ACCOUNT_SID = get_env_var('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = get_env_var('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NO = get_env_var('TWILIO_PHONE_NO')


# GOOGLE
GOOGLE_GEOLOCATION_API_KEY = get_env_var('GOOGLE_GEOLOCATION_API_KEY')

# Baza Signup
# In km
MAXIMUM_ALLOWED_DISTANCE_FOR_SIGNUP = int(get_env_var(
    'MAXIMUM_ALLOWED_DISTANCE_FOR_SIGNUP'))


# Baza Site Owners emails
# If multiple separate by comma
SITE_OWNER_EMAILS = get_env_var('SITE_OWNER_EMAILS')

# Taiga Issue Creator
TAIGA_USERNAME = get_env_var('TAIGA_USERNAME')
TAIGA_PASSWORD = get_env_var('TAIGA_PASSWORD')

# Bleach sanitize
BLEACH_VALID_TAGS = ['p', 'b', 'i', 'u',
                     'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                     'strike', 'ul', 'li', 'ol', 'br',
                     'span', 'blockquote', 'hr', 'a', 'img']
BLEACH_VALID_ATTRS = {
    'span': ['style', 'class'],
    'p': ['align', ],
    'a': ['href', 'rel'],
    'img': ['src', 'alt', 'style'],
}
BLEACH_VALID_STYLES = ['color', 'cursor', 'float', 'margin']


# Paypal API
PAYPAL_MODE = get_env_var("PAYPAL_MODE")
PAYPAL_CLIENT_ID = get_env_var('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = get_env_var('PAYPAL_CLIENT_SECRET')
PAYPAL_CANCEL_URL = get_env_var('PAYPAL_CANCEL_URL')
PAYPAL_RETURN_URL = get_env_var('PAYPAL_RETURN_URL')

INTERNAL_WEBHOOK_KEY = get_env_var('INTERNAL_WEBHOOK_KEY')

# Coinbase
COINBASE_API_KEY = get_env_var('COINBASE_API_KEY')
COINBASE_WEBHOOK_SECRET = get_env_var('COINBASE_WEBHOOK_SECRET')

# Facebook
FACEBOOK_APP_ID = get_env_var('FACEBOOK_APP_ID')
