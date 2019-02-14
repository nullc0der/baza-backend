from django.apps import AppConfig


class CoinpurchaseConfig(AppConfig):
    name = 'coinpurchase'

    def ready(self):
        import coinpurchase.signals
