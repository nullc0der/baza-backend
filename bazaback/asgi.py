"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
import django
from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bazaback.settings")
django.setup()

# SENTRY_ENABLED_IN = ['production', 'beta', 'api']
application = get_default_application()

# if os.environ.get('SITE_TYPE') in SENTRY_ENABLED_IN:
#    from raven.contrib.django.raven_compat.middleware.wsgi import Sentry
#    application = Sentry(get_default_application())
