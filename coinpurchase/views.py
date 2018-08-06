from django.conf import settings

from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from stripepayment.utils import StripePayment

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
            stripe_payment = StripePayment(
                user=request.user,
                fullname=None
            )
            payment = stripe_payment.process_payment(
                token=serializer.validated_data['stripe_token'],
                payment_type='coin_purchase',
                amount=serializer.validated_data['price'],
                message='',
                receipt_email=request.user.email if request.user.email else None
            )
            if payment.is_success:
                CoinPurchase.objects.create(
                    user=request.user,
                    price=serializer.validated_data['price'],
                    amount=serializer.validated_data['price'] *
                    get_coin_value(serializer.validated_data['coin_name']),
                    coin_name=serializer.validated_data['coin_name'],
                    stripe_payment=payment
                )
                return Response()
            return Response({
                'non_field_errors': [
                    'There is an issue processing your payment,'
                    'please try later']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST)
