from django.conf import settings
import paypalrestsdk

paypal_api = paypalrestsdk.Api({
    'mode': settings.PAYPAL_MODE,
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_CLIENT_SECRET
})


def create_payment(amount):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "application_context": {
            "landing_page": "Billing",
            "shipping_preference": "NO_SHIPPING"
        },
        "transactions": [{
            "amount": {
                "total": amount,
                "currency": "USD"
            }
        }],
        "redirect_urls": {
            "return_url": settings.PAYPAL_RETURN_URL,
            "cancel_url": settings.PAYPAL_CANCEL_URL
        }
    }, api=paypal_api)

    if payment.create():
        return payment.to_dict()['id']
    return False


def execute_payment(payment_id, payer_id):
    payment = paypalrestsdk.Payment(api=paypal_api).find(payment_id)
    if payment.execute({'payer_id': payer_id}):
        return True
    return False
