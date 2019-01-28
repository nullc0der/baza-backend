from django.db import models
from django.contrib.auth.models import User

from coinbasepay.models import Charge
# Create your models here.


class Donation(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='donations', null=True)
    amount = models.FloatField()
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_no = models.CharField(max_length=20, default='')
    is_pending = models.BooleanField(default=True)
    logged_ip = models.GenericIPAddressField(null=True)
    coinbase_charge = models.OneToOneField(
        Charge, on_delete=models.SET_NULL, null=True
    )
    donated_on = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name
