from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    'corsheaders',
]

MIDDLEWARE.insert(2, 'corsheaders.middleware.CorsMiddleware')

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# CORS

CORS_ORIGIN_WHITELIST = [
    'localhost:5100'
]

CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'x-csrftoken',
    'access-token'
)


# CELERY
CELERY_BROKER_URL = 'redis://' + get_env_var('REDIS_HOST') + ':6379/1'
CELERY_RESULT_BACKEND = 'redis://' + get_env_var('REDIS_HOST') + ':6379/1'

MJML_BACKEND_MODE = 'tcpserver'
MJML_TCPSERVERS = [
    ('127.0.0.1', 28101)
]
