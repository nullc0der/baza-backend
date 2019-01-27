from django.apps import AppConfig


class DonationConfig(AppConfig):
    name = 'donation'

    def ready(self):
        import donation.signals
