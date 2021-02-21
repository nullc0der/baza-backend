from django.conf import settings
from django.template import loader
from django.core.mail import EmailMultiAlternatives


def send_main_wallet_low_balance_email_to_admins() -> bool:
    email_template = loader.get_template(
        'webwallet/main_wallet_low_balance.html')
    server = 'Live' if settings.SITE_TYPE == 'live' else 'Beta'
    wallet_address = settings.PROXC_TO_REAL_FROM_ADDRESS
    msg = EmailMultiAlternatives(
        subject='%s Server Main Wallet Balance Is Low' % server,
        body='Hi\n, The main wallet of %s server is low,\n'
        ' please send fund to this address %s' % (server, wallet_address),
        from_email='system@baza.foundation',
        to=settings.SITE_OWNER_EMAILS
    )
    msg.attach_alternative(email_template.render({
        'server': server,
        'wallet_address': wallet_address
    }), "text/html")
    msg.send()
