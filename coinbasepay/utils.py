from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from coinbase_commerce.client import Client
from coinbase_commerce.error import CoinbaseError

from authclient.utils import AuthHelperClient
from coinbasepay.models import Charge, ChargePricing
from coinpurchase.utils import get_user_access_token

URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


def create_charge(
        amount, charge_name, charge_description,
        charged_for, charged_user=None):
    coinbase_commerce_client = Client(api_key=settings.COINBASE_API_KEY)
    try:
        charge = coinbase_commerce_client.charge.create(
            name=charge_name,
            description=charge_description,
            pricing_type='fixed_price',
            local_price={
                'amount': amount,
                'currency': 'USD'
            },
            metadata={
                'user_id': charged_user.id if charged_user else 'Anonymous',
                'charged_for': charged_for
            }
        )
        chargepricing = ChargePricing(
            local=charge['pricing']['local']['amount'],
            bitcoin=charge['pricing']['bitcoin']['amount'],
            bitcoincash=charge['pricing']['bitcoincash']['amount'],
            litecoin=charge['pricing']['litecoin']['amount'],
            ethereum=charge['pricing']['ethereum']['amount']
        )
        chargepricing.save()
        charge_obj = Charge(
            charge_id=charge['id'],
            charge_code=charge['code'],
            charged_user=charged_user,
            charged_for=charged_for,
            pricing=chargepricing,
            created_at=charge['created_at'],
            expires_at=charge['expires_at']
        )
        charge_obj.save()
        return charge_obj.charge_code
    except CoinbaseError:
        return False


def send_email_if_unresolved_charge(charge_id):
    charge = Charge.objects.get(id=charge_id)
    if charge.status == 'UNRESOLVED':
        access_token = get_user_access_token(charge.charged_user)
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/useremails/'
        )
        res_status, data = authhelperclient.get_user_emails(access_token)
        if res_status == 200:
            primary_emails = [
                email for email in data
                if email['primary'] and email['verified']]
            if len(primary_emails):
                email_template = loader.get_template(
                    'coinbasepay/unresolvedcharge.html')
                msg = EmailMultiAlternatives(
                    subject='Charge Unresolved',
                    body='',
                    from_email='unresolvedcharge-noreply@baza.foundation',
                    to=[primary_emails[0]['email']]
                )
                msg.attach_alternative(email_template.render({
                    'username': charge.charged_user.profile.username
                    or charge.charged_user.username,
                    'charge_id': charge.charge_code,
                    'status': charge.charge_status_context
                }), 'text/html')
                msg.send()
