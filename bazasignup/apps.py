from django.apps import AppConfig


class BazasignupConfig(AppConfig):
    name = 'bazasignup'

    def ready(self):
        import bazasignup.signals
