from django.conf import settings

from bazasignup.models import BazaSignup
from webwallet.api_wrapper import ApiWrapper
from proxcdb.models import ProxcTransaction


def send_fund_from_proxc_to_real_wallet(proxcaccount, to_address, amount):
    apiwrapper = ApiWrapper()
    res = apiwrapper.send_subwallet_transaction(
        to_address, settings.PROXC_TO_REAL_FROM_ADDRESS, amount)
    print(res.status_code, res.content)
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
def send_daily_distribution():
    bazasignups = BazaSignup.objects.filter(
        status='approved', on_distribution=True, verified_date__isnull=False)
    for bazasignup in bazasignups:
        transaction = ProxcTransaction(
            to_account=bazasignup.user.proxcaccount,
            message='daily_baza_distribution',
            amount=5,
            should_substract_txfee=False
        )
        transaction.save()
    return 'sent {} to {} user'.format(bazasignups.count() * 5, bazasignups.count())
