from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from stripepayment.models import Payment
from proxcdb.models import ProxcAccount, ProxcTransaction


class CoinPurchase(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='coinpurchases')
    amount = models.FloatField()
    price = models.FloatField(null=True)
    currency = models.CharField(max_length=10, default='')
    coin_name = models.CharField(max_length=100, default='')
    stripe_payment = models.OneToOneField(
        Payment, on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=CoinPurchase)
def add_wallet_balance(sender, instance, created, **kwargs):
    if created and instance.coin_name == 'proxcdb':
        proxcaccount, c = ProxcAccount.objects.get_or_create(
            user=instance.user)
        proxcaccount.balance += instance.amount
        proxcaccount.save()
        proxctransaction = ProxcTransaction(
            to_account=proxcaccount,
            message='Fundraiser reward',
            amount=instance.amount
        )
        proxctransaction.save()
