import json
import stripe

from django.conf import settings

from stripepayment.models import Payment


class StripePayment(object):
    def __init__(self, user=None, fullname=None):
        self.user = user
        self.fullname = fullname

    def process_payment(
            self, token, payment_type='',
            amount=0, message='', receipt_email=None):
        payment = Payment(
            amount=amount,
            payment_type=payment_type,
            message=message
        )
        if self.user:
            payment.user = self.user
        if self.fullname:
            payment.name = self.fullname
        payment.save()
        if amount >= 1:
            amount = int(amount * 100)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                description=payment_type,
                metadata={
                    "payment_id": payment.id,
                    "message": payment.message
                },
                source=token,
                receipt_email=receipt_email
            )
            payment.charge_id = charge.id
            payment.is_success = True
            payment.save()
        except Exception as e:
            body = e.json_body
            err = body['error']
            payment.fail_reason = err['message']
            payment.save()
        return payment

    def retrive_charge(self, payment):
        charge_id = payment.charge_id
        try:
            charge = stripe.Charge.retrieve(charge_id)
            return charge
        except:
            return None
