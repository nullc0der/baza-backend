import json
import hmac
import hashlib

from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView

from ekatagp.models import PaymentForm


class PaymentSuccessWebhook(APIView):
    def post(self, request, format=None):
        message = f"{request.body['payment_id']}" + \
            f"{request.body['wallet_address']}" + \
            f"{request.body['amount_received']}"
        signature = hmac.new(
            settings.EKATA_GATEWAY_PROCESSOR_PROJECT_API_SECRET.encode(),
            message.encode(),
            hashlib.sha256).hexdigest()
        if signature == request.body['signature']:
            form = PaymentForm.objects.get(form_id=request.body['form_id'])
            form.is_payment_success = True
            form.payment_payload = json.dumps(request.body)
            form.save()
            donation = form.donation
            donation.is_pending = False
            donation.save()
        return Response()
