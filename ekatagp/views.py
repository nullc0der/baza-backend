import json
import hmac
import hashlib

from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView

from ekatagp.models import PaymentForm


class PaymentSuccessWebhook(APIView):
    def post(self, request, format=None):
        message = f"{request.data['payment_id']}" + \
            f"{request.data['wallet_address']}" + \
            f"{request.data['amount_received']}"
        signature = hmac.new(
            settings.EKATA_GATEWAY_PROCESSOR_PROJECT_API_SECRET.encode(),
            message.encode(),
            hashlib.sha256).hexdigest()
        if signature == request.data['signature']:
            form = PaymentForm.objects.get(form_id=request.data['form_id'])
            form.is_payment_success = True
            form.payment_payload = json.dumps(request.data)
            form.save()
            donation = form.donation
            donation.is_pending = False
            donation.save()
        return Response()
