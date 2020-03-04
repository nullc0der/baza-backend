import os

from django.apps import AppConfig


class WebWalletConfig(AppConfig):
    name = 'webwallet'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) == 'true':
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
