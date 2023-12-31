from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.timezone import now

from oauth2_provider.models import get_access_token_model

from authclient.utils import AuthHelperClient
from coinpurchase.models import CoinPurchase
from proxcdb.models import ProxcAccount, ProxcTransaction

URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


def get_coin_value(coin_name):
    """This function will return coin value per dollar
    Currently it returns a static value, later we need to implement
    method to retrive value
    """
    return 0.01000


def get_user_access_token(user):
    AccessToken = get_access_token_model()
    accesstokens = AccessToken.objects.filter(user=user)
    for accesstoken in accesstokens:
        if accesstoken.expires > now():
            return accesstoken.token
    return


def purchase_has_exception(purchase):
    if purchase.coinbase_charge:
        if purchase.coinbase_charge.status == 'UNRESOLVED':
            return True
    return False


def get_purchase_info(purchase):
    coinbase_charge = purchase.coinbase_charge
    status = coinbase_charge.status
    if status == 'UNRESOLVED':
        status = 'MULTIPLE' if coinbase_charge.payments.count(
        ) > 1 else coinbase_charge.charge_status_context
    return {
        'username': coinbase_charge.charged_user.profile.username or
        coinbase_charge.charged_user.username,
        'amount': purchase.amount,
        'order_number': coinbase_charge.charge_code,
        'order_date': coinbase_charge.created_at,
        'receipt_url': coinbase_charge.get_receipt_url(),
        'status': status,
        'received_amount': purchase.price,
        'expected_amount': coinbase_charge.pricing.local
    }


def send_coinpurchase_confirm_email(coinpurchase):
    access_token = get_user_access_token(coinpurchase.user)
    authhelperclient = AuthHelperClient(
        URL_PROTOCOL +
        settings.CENTRAL_AUTH_INTROSPECT_URL +
        '/authhelper/useremails/'
    )
    res_status, data = authhelperclient.get_user_emails(access_token)
    if res_status == 200:
        primary_emails = [
            email for email in data if email['primary'] and email['verified']]
        if len(primary_emails):
            email_template = loader.get_template(
                'coinpurchase/purchaseconfirm.html')
            msg = EmailMultiAlternatives(
                subject='Baza Token Reward',
                body='Hello %s'
                'Thank you for participating in Baza Foundation fundraiser'
                'You\'ve got %s BAZ in your account as reward' % (
                    coinpurchase.user.profile.username
                    or coinpurchase.user.username,
                    coinpurchase.amount),
                from_email='fundraiser-noreply@baza.foundation',
                to=[primary_emails[0]['email']]
            )
            msg.attach_alternative(email_template.render({
                'purchase_info': get_purchase_info(coinpurchase),
                'has_exception': purchase_has_exception(
                    coinpurchase)
            }), 'text/html')
            msg.send()


def create_proxc_transaction(coinpurchase_id):
    coinpurchase = CoinPurchase.objects.get(id=coinpurchase_id)
    proxcaccount, c = ProxcAccount.objects.get_or_create(
        user=coinpurchase.user)
    proxctransaction = ProxcTransaction(
        to_account=proxcaccount,
        message='Fundraiser reward',
        amount=coinpurchase.amount,
        coinpurchase=coinpurchase
    )
    proxctransaction.save()
    send_coinpurchase_confirm_email(coinpurchase)
