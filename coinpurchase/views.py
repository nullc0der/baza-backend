from django.conf import settings

from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from coinpurchase.models import CoinPurchase
from coinpurchase.serializers import CoinPurchaseSerializer
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


class ProcessCoinPurchase(views.APIView):
    """
    This API will process coin purchase
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        serializer = CoinPurchaseSerializer(data=request.data)
        if serializer.is_valid():
            CoinPurchase.objects.create(
                user=request.user,
                price=serializer.validated_data['price'],
                amount=serializer.validated_data['price'] *
                get_coin_value(serializer.validated_data['coin_name']),
                coin_name=serializer.validated_data['coin_name']
            )
            return Response()
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST)
