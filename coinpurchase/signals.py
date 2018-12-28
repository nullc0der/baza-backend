from django.db.models.signals import post_save
from django.dispatch import receiver

from coinbasepay.models import Charge
from coinpurchase.models import CoinPurchase
from coinpurchase.utils import get_coin_value
from coinpurchase.tasks import task_create_proxc_transaction


STATUSES = ['CONFIRMED', 'UNRESOLVED']


def get_price_and_amount(payments):
    price = 0
    for payment in payments:
        price += float(payment.localamount)
    # TODO: Remove print function
    print(price)
    return price, price * get_coin_value('proxcdb')


@receiver(post_save, sender=CoinPurchase)
def add_wallet_balance(sender, instance, created, **kwargs):
    if created and instance.coin_name == 'proxcdb':
        task_create_proxc_transaction.delay(instance.id)


@receiver(post_save, sender=Charge)
def create_coinpurchase(sender, instance, created, **kwargs):
    if instance.charged_for == 'PROXC_COIN_PURCHASE':
        if instance.status in STATUSES\
                and not instance.charged_for_related_task_is_done:
            price, amount = get_price_and_amount(instance.payments.all())
            CoinPurchase.objects.create(
                user=instance.charged_user,
                price=price,
                amount=amount,
                coin_name='proxcdb',
                coinbase_charge=instance
            )
            instance.charged_for_related_task_is_done = True
            instance.save()
