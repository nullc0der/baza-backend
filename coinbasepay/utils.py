from django.conf import settings

from coinbase_commerce.client import Client
from coinbase_commerce.error import CoinbaseError

from coinbasepay.models import Charge, ChargePricing

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


def resolve_charge(charge_id):
    charge = Charge.objects.get(id=charge_id)
    coinbase_commerce_client = Client(api_key=settings.COINBASE_API_KEY)
    try:
        coinbase_commerce_client.post(
            'charges/%s/resolve' % charge.charge_code)
        charge.status = 'RESOLVED'
        charge.save()
    except CoinbaseError:
        pass
