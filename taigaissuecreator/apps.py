from __future__ import unicode_literals

from django.apps import AppConfig


class TaigaissuecreatorConfig(AppConfig):
    name = 'taigaissuecreator'

    def ready(self):
        import taigaissuecreator.signals  # noqa
