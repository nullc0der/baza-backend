from django.db.models.signals import post_save
from django.dispatch import receiver

from coinbasepay.models import Charge
from coinpurchase.models import CoinPurchase
from coinpurchase.utils import get_coin_value
from coinpurchase.tasks import task_create_proxc_transaction


@receiver(post_save, sender=CoinPurchase)
def add_wallet_balance(sender, instance, created, **kwargs):
    if created and instance.coin_name == 'proxcdb':
        task_create_proxc_transaction.delay(instance.id)


@receiver(post_save, sender=Charge)
def create_coinpurchase(sender, instance, created, **kwargs):
    if instance.status == 'CONFIRMED'\
            and not instance.charged_for_related_task_is_done:
        CoinPurchase.objects.create(
            user=instance.charged_user,
            price=instance.pricing.local,
            amount=float(instance.pricing.local) * get_coin_value('proxcdb'),
            coin_name='proxcdb'
        )
        instance.charged_for_related_task_is_done = True
        instance.save()
