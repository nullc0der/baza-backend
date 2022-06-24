# NOTE: There is multiple request to open wallet, and sometime the wallet was
# not actually open or crashes because of
# some issue which requires a wallet reopen
from decimal import Decimal

import requests

from django.conf import settings

data = {
    'daemonHost': settings.COIN_DAEMON_HOST,
    'daemonPort': int(settings.COIN_DAEMON_PORT),
    'filename': settings.WALLET_FILENAME,
    'password': settings.WALLET_PASSWORD
}

ATOMIC = Decimal('0.000001')


def from_atomic(amount: int) -> Decimal:
    return (Decimal(amount) * ATOMIC).quantize(ATOMIC)


def to_atomic(amount: Decimal):
    return int(amount * 10 ** 6)


class ApiWrapper(object):
    wallet_is_open = False

    def get_request_function(self, req_method):
        if req_method == 'POST':
            return requests.post
        if req_method == 'DELETE':
            return requests.delete
        if req_method == 'PUT':
            return requests.put
        return requests.get

    def get_api_response(self, req_method, api_endpoint, data=None):
        url = settings.WALLET_API_URL + api_endpoint
        headers = {
            'X-API-KEY': settings.WALLET_API_KEY
        }
        request_function = self.get_request_function(req_method)
        if data:
            return request_function(url, headers=headers, json=data)
        return request_function(url, headers=headers)

    def get_wallet_status(self):
        return self.get_api_response('GET', '/status')

    def open_wallet(self):
        return self.get_api_response('POST', '/wallet/open', data)

    def create_wallet(self):
        return self.get_api_response('POST', '/wallet/create', data)

    def close_wallet(self):
        return self.get_api_response('DELETE', '/wallet')

    def save_wallet(self):
        return self.get_api_response('PUT', '/save')

    def create_subwallet(self):
        if self.wallet_is_open:
            res = self.get_api_response('POST', '/addresses/create')
            self.save_wallet()
            return res

    def create_integrated_address(self, address, payment_id):
        if self.wallet_is_open:
            return self.get_api_response(
                'GET', '/addresses/{}/{}'.format(address, payment_id))

    def get_subwallet_transactions(
            self, address, start_height=0, end_height=None):
        if self.wallet_is_open:
            if not end_height:
                res = self.get_wallet_status()
                if res.status_code == 200:
                    end_height = res.json()['walletBlockCount']
            return self.get_api_response(
                'GET', '/transactions/address/{}/{}/{}'.format(
                    address, start_height, end_height)
            )

    def send_subwallet_transaction(
            self, destination_address, source_address, amount):
        data = {
            'destinations': [
                {
                    'address': destination_address,
                    'amount': amount
                }
            ],
            'sourceAddresses': [source_address],
            'changeAddress': source_address
        }
        if self.wallet_is_open:
            return self.get_api_response(
                'POST', '/transactions/send/advanced',
                data
            )

    def get_subwallet_balance(self, address):
        if self.wallet_is_open:
            return self.get_api_response(
                'GET', '/balance/{}'.format(address)
            )

    def validate_address(self, address):
        if self.wallet_is_open:
            return self.get_api_response(
                'POST', '/addresses/validate', {'address': address}
            )
