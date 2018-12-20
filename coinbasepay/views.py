from django.conf import settings

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from coinbase_commerce.webhook import Webhook
from coinbase_commerce.error import (
    WebhookInvalidPayload, SignatureVerificationError)

from coinbasepay.models import Charge
from coinbasepay.utils import create_charge
from coinbasepay.dicts import CHARGE


class IntializeCoinbaseChargeView(views.APIView):
    """
    This view will be used to initialize a coinbase transaction
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, charge_type, format=None):
        charge_id = create_charge(
            amount=request.data.get('amount'),
            charge_name=CHARGE[charge_type]['name'],
            charge_description=CHARGE[charge_type]['description'],
            charged_for=CHARGE[charge_type]['charged_for'],
            charged_user=request.user)
        if charge_id:
            return Response({'charge_id': charge_id})
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CoinbaseWebhookView(views.APIView):
    def process_confirmed_charge(self, event):
        try:
            charge = Charge.objects.get(charge_code=event['data']['code'])
            charge.status = 'CONFIRMED'
            charge.save()
        except Charge.DoesNotExist:
            pass

    def process_failed_charge(self, event):
        try:
            charge = Charge.objects.get(charge_code=event['data']['code'])
            charge.status = 'FAILED'
            charge.save()
        except Charge.DoesNotExist:
            pass

    def process_delayed_charge(self, event):
        try:
            charge = Charge.objects.get(charge_code=event['data']['code'])
            for t in event['data']['timeline']:
                if t['status'] == 'COMPLETED':
                    charge.status = 'CONFIRMED'
                    charge.save()
        except Charge.DoesNotExist:
            pass

    def post(self, request, format=None):
        try:
            event = Webhook.construct_event(
                request.body.decode('utf-8'),
                request.META['HTTP_X_CC_WEBHOOK_SIGNATURE'],
                settings.COINBASE_WEBHOOK_SECRET)
        except (WebhookInvalidPayload, SignatureVerificationError):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if event.type == 'charge:confirmed':
            self.process_confirmed_charge(event)
        if event.type == 'charge:failed':
            self.process_failed_charge(event)
        if event.type == 'charge:delayed':
            self.process_delayed_charge(event)
        return Response()
