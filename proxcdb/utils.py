from django.conf import settings

from bazasignup.models import BazaSignup
from webwallet.api_wrapper import ApiWrapper
from proxcdb.models import ProxcTransaction


def send_fund_from_proxc_to_real_wallet(proxcaccount, to_address, amount):
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
    return 'sent {} to {} user'.format(bazasignups.count() * 0.003472, bazasignups.count())
