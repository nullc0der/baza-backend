from django.apps import AppConfig
from django.core.cache import cache


class AuthclientConfig(AppConfig):
    name = 'authclient'

    def ready(self):
        cache.set('user_auths', {}, None)
