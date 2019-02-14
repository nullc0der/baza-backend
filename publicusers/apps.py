from django.apps import AppConfig
from django.core.cache import cache


class PublicusersConfig(AppConfig):
    name = 'publicusers'

    def ready(self):
        cache.set('online_users', [], None)
