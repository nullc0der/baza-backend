from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User


def get_random_id():
    return get_random_string(length=30)


class ProxcAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=100.000000)


class ProxcTransaction(models.Model):
    account = models.ForeignKey(
        ProxcAccount,
        related_name='proxc_transaction_form',
        on_delete=models.SET_NULL,
        null=True
    )
    to_account = models.ForeignKey(
        ProxcAccount,
        related_name='proxc_transaction_to',
        on_delete=models.SET_NULL,
        null=True
    )
    message = models.TextField(null=True)
    txid = models.TextField(default=get_random_id)
    status = models.CharField(default='success', max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()


@receiver(post_save, sender=User)
def create_user_account(sender, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        proxcaccount = ProxcAccount(user=user)
        proxcaccount.save()


@receiver(post_save, sender=ProxcTransaction)
def calculate_amount(sender, **kwargs):
    transaction = kwargs['instance']
    account = transaction.account
    account.balance -= transaction.amount
    to_account = transaction.to_account
    to_account.balance += transaction.amount
    account.save()
    to_account.save()
