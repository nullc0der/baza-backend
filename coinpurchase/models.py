from django.db import models
from django.contrib.auth.models import User

from coinbasepay.models import Charge


class CoinPurchase(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='coinpurchases')
    amount = models.FloatField()
    price = models.FloatField(null=True)
    currency = models.CharField(max_length=10, default='')
    coin_name = models.CharField(max_length=100, default='')
    coinbase_charge = models.OneToOneField(
        Charge, on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return self.user.username
