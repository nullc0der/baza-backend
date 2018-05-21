"""
WSGI config for bazaback project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bazaback.settings")

SENTRY_ENABLED_IN = ['production', 'beta']
application = get_wsgi_application()

if os.environ.get('SITE_TYPE') in SENTRY_ENABLED_IN:
    from raven.contrib.django.raven_compat.middleware.wsgi import Sentry
    application = Sentry(get_wsgi_application())
