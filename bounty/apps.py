from django.apps import AppConfig


class BountyConfig(AppConfig):
    name = 'bounty'

    def ready(self):
        import bounty.signals
