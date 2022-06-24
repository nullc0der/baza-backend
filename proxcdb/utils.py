from django.conf import settings

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from bazasignup.models import BazaSignup

from webwallet.api_wrapper import ApiWrapper
from webwallet.tasks import task_send_main_wallet_low_balance_email_to_admins

from proxcdb.models import ProxcTransaction

channel_layer = get_channel_layer()


def check_main_wallet_have_sufficient_balance(requested_amount: int) -> bool:
    apiwrapper = ApiWrapper()
    res = apiwrapper.get_subwallet_balance(settings.PROXC_TO_REAL_FROM_ADDRESS)
    if res.status_code == 200:
        if res.json()['unlocked'] > requested_amount:
            return True
        task_send_main_wallet_low_balance_email_to_admins.delay()
    return False


def send_fund_from_proxc_to_real_wallet(proxcaccount, to_address, amount):
    # NOTE: The atomic conversion might not be accurate, need to check
    # maybe use decimal where appropriate
    if check_main_wallet_have_sufficient_balance(amount * 1000000):
        apiwrapper = ApiWrapper()
        res = apiwrapper.send_subwallet_transaction(
            to_address, settings.PROXC_TO_REAL_FROM_ADDRESS, amount * 1000000)
        if res.status_code == 200:
            data = res.json()
            proxctransaction = ProxcTransaction(
                account=proxcaccount,
                message='proxc_to_real_baza_transaction',
                txid=data['transactionHash'],
                amount=amount
            )
            proxctransaction.save()
            return data['transactionHash']


# TODO: Add email
# TODO: Refactor this function to baza signup
def send_per_minute_distribution():
    bazasignups = BazaSignup.objects.filter(
        status='approved', on_distribution=True, verified_date__isnull=False)
    for bazasignup in bazasignups:
        transaction = ProxcTransaction(
            to_account=bazasignup.user.proxcaccount,
            message='per_minute_baza_distribution',
            amount=0.003472,
            should_substract_txfee=False
        )
        transaction.save()
        async_to_sync(channel_layer.group_send)(
            'notifications_for_%s' % bazasignup.user.id,
            {
                'type': 'notification.message',
                'message': {
                    'type': 'add_baza_distribution_balance',
                    'data': {'balance': 0.003472}
                }
            }
        )
    return 'sent {} to {} user'.format(
        bazasignups.count() * 0.003472, bazasignups.count())
