from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Payment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='payments', null=True)
    name = models.CharField(default='', max_length=250)
    amount = models.PositiveIntegerField(
        null=True, blank=True
    )
    is_success = models.BooleanField(default=False)
    message = models.CharField(default='', max_length=250)
    payment_type = models.CharField(default='', max_length=100)
    fail_reason = models.CharField(default='', max_length=300)
    charge_id = models.CharField(default='', max_length=200)
    date = models.DateField(auto_now_add=True, null=True)
