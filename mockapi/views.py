from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

# Create your views here.


class WalletAccounts(APIView):
    """
    API to get mock version of walletaccounts
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        datas = [
            {
                'id': 1,
                'name': 'Baza',
                'balance': request.user.proxcaccount.balance,
                'image': '/public/img/baza_logo.svg'
            }
            # {
            #     'id': 2,
            #     'name': 'Monero',
            #     'balance': 'xxxxx',
            #     'image': '/public/img/monero.svg'
            # },
            # {
            #     'id': 3,
            #     'name': 'Bitcoin',
            #     'balance': 'xxxxx',
            #     'image': '/public/img/bitcoin.svg'
            # },
            # {
            #     'id': 4,
            #     'name': 'Ether',
            #     'balance': 'xxxxx',
            #     'image': '/public/img/ethereum.svg'
            # }
        ]
        return Response(data=datas)


class WalletTransaction(APIView):
    """
    This mock API returns random
    transactions data(Currently empty data)
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        return Response()
