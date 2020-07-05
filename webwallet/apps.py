import os

from django.apps import AppConfig
from django.conf import settings


class WebWalletConfig(AppConfig):
    name = 'webwallet'

    def ready(self):
        if settings.SITE_TYPE != 'local':
            from webwallet.api_wrapper import ApiWrapper
            apiwrapper = ApiWrapper()
            res = apiwrapper.open_wallet()
            if res.status_code == 403:
                apiwrapper.close_wallet()
                res = apiwrapper.open_wallet()
            if res.status_code == 400 and res.json()['errorCode'] == 1:
                res = apiwrapper.create_wallet()
            if res.status_code == 200:
                ApiWrapper.wallet_is_open = True
