from django.conf import settings
from django.template import loader
from django.core.mail import EmailMultiAlternatives


def send_main_wallet_low_balance_email_to_admins() -> bool:
    email_template = loader.get_template(
        'webwallet/main_wallet_low_balance.html')
    server = 'Live' if settings.SITE_TYPE == 'production' else 'Beta'
    wallet_address = settings.PROXC_TO_REAL_FROM_ADDRESS
    for email_id in settings.SITE_OWNER_EMAILS:
        msg = EmailMultiAlternatives(
            subject='%s Server Main Wallet Balance Is Low' % server,
            body='Hi\n, The main wallet of %s server is low,\n'
            ' please send fund to this address %s' % (
                server.lower(), wallet_address),
            from_email='system@baza.foundation',
            to=[email_id]
        )
        msg.attach_alternative(email_template.render({
            'server': server,
            'wallet_address': wallet_address
        }), "text/html")
        msg.send()
