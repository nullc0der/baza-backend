from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class WalletAccounts(APIView):
    """
    API to get mock version of walletaccounts
    """

    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        datas = [
            {
                'id': 1,
                'name': 'Baza',
                'image': '/public/img/baza_logo.svg'
            },
            {
                'id': 2,
                'name': 'Monero',
                'image': '/public/img/monero.svg'
            },
            {
                'id': 3,
                'name': 'Bitcoin',
                'image': '/public/img/bitcoin.svg'
            },
            {
                'id': 4,
                'name': 'Ether',
                'image': '/public/img/ethereum.svg'
            }
        ]
        return Response(data=datas)


class WalletTransaction(APIView):
    """
    This mock API returns random
    transactions data(Currently empty data)
    """

    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        return Response()
