import requests
from decimal import Decimal

from django.conf import settings
from django.utils.dateparse import parse_datetime

from ekatagp.models import PaymentForm


def create_payment_form(amount):
    data = {
        'amount_requested': int(Decimal(amount) * 100),
        'fiat_currency': 'USD',
        'project_id': settings.EKATA_GATEWAY_PROCESSOR_PROJECT_ID,
        'api_key': settings.EKATA_GATEWAY_PROCESSOR_PROJECT_API_KEY
    }
    res = requests.post(
        f'{settings.EKATA_GATEWAY_PROCESSOR_API_URL}/payment-form/create',
        json=data)
    if res.status_code == 200:
        data = res.json()
        payment_form = PaymentForm.objects.create(
            form_id=data['id'],
            created_on=parse_datetime(data['created_on']))
        return payment_form.form_id
