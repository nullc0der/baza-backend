import channels.apps
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from .base import *

DEBUG = False

ALLOWED_HOSTS = [get_env_var('HOST')]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_var('DJANGO_DATABASE_NAME'),
        'USER': get_env_var('DJANGO_DATABASE_USERNAME'),
        'PASSWORD': get_env_var('DJANGO_DATABASE_PASSWORD'),
        'HOST': get_env_var('DJANGO_DATABASE_HOST'),
        'PORT': '',
    }
}

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = get_env_var('DJANGO_EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_HOST_USER = get_env_var('DJANGO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_var('DJANGO_EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True

SECURE_BROWSER_XSS_FILTER = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

X_FRAME_OPTIONS = 'DENY'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Sentry

sentry_sdk.init(
    dsn=get_env_var("SENTRY_DSN"),
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,

    # By default the SDK will try to use the SENTRY_RELEASE
    # environment variable, or infer a git commit
    # SHA as release, however you may want to set
    # something more human-readable.
    # release="myapp@1.0.0",
)

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

MJML_BACKEND_MODE = 'tcpserver'
MJML_TCPSERVERS = [
    ('mjml', 28101)
]
