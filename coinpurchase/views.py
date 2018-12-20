from rest_framework import views
from rest_framework.response import Response

from coinpurchase.models import CoinPurchase
from coinpurchase.utils import get_coin_value


class GetCoinValue(views.APIView):
    """
    This API will return current price of a coin
    Required params:
        * coin_name
    """

    def get(self, request, format=None):
        value = get_coin_value(request.query_params['coin_name'])
        return Response(value)


class GetTotalCoinPurchased(views.APIView):
    """
    This API will send total purchased coin
    """

    def get(self, request, format=None):
        amount = 0
        for coinpurchase in CoinPurchase.objects.filter(coin_name='proxcdb'):
            amount += coinpurchase.amount
        return Response({'total_purchased': amount})
