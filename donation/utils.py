from django.template import loader
from django.core.mail import EmailMultiAlternatives

from donation.models import Donation


def donation_has_exception(donation):
    if donation.coinbase_charge:
        if donation.coinbase_charge.status == 'UNRESOLVED':
            return True
    return False


def get_donation_info(donation):
    coinbase_charge = donation.coinbase_charge
    status = coinbase_charge.status
    if status == 'UNRESOLVED':
        status = 'MULTIPLE' if coinbase_charge.payments.count(
        ) > 1 else coinbase_charge.charge_status_context
    return {
        'amount': donation.amount,
        'order_number': coinbase_charge.charge_code,
        'order_date': coinbase_charge.created_at,
        'receipt_url': coinbase_charge.get_receipt_url(),
        'status': status,
        'received_amount': donation.amount,
        'expected_amount': coinbase_charge.pricing.local
    }


def send_donation_confirm_email(donation_id):
    donation = Donation.objects.get(id=donation_id)
    if donation.email:
        email_template = loader.get_template(
            'donation/donationconfirm.html')
        msg = EmailMultiAlternatives(
            subject='Baza Foundation Donation',
            body='Thank you for donating to Baza Foundation',
            from_email='donation-noreply@baza.foundation',
            to=[donation.email]
        )
        msg.attach_alternative(email_template.render({
            'donation_info': get_donation_info(donation),
            'has_exception': donation_has_exception(donation)
        }), 'text/html')
        msg.send()
