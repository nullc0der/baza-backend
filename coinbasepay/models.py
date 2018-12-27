from django.db import models
from django.contrib.auth.models import User


class ChargePricing(models.Model):
    local = models.CharField(max_length=100, default='')
    bitcoin = models.CharField(max_length=100, default='')
    bitcoincash = models.CharField(max_length=100, default='')
    litecoin = models.CharField(max_length=100, default='')
    ethereum = models.CharField(max_length=100, default='')


class Charge(models.Model):
    CHARGE_STATUS_CHOICES = (
        ('NEW', 'NEW'),
        ('CONFIRMED', 'CONFIRMED'),
        ('FAILED', 'FAILED'),
        ('UNRESOLVED', 'UNRESOLVED'),
        ('RESOLVED', 'RESOLVED')
    )
    CHARGED_FOR_CHOICES = (
        ('PROXC_COIN_PURCHASE', 'PROXC_COIN_PURCHASE'),
        ('DONATION', 'DONATION')
    )
    CHARGE_STATUS_CONTEXT_CHOICES = (
        ('OVERPAID', 'OVERPAID'),
        ('UNDERPAID', 'UNDERPAID'),
        ('MULTIPLE', 'MULTIPLE'),
        ('DELAYED', 'DELAYED'),
        ('MANUAL', 'MANUAL'),
        ('OTHER', 'OTHER')
    )
    charge_id = models.CharField(max_length=100)
    charge_code = models.CharField(max_length=100, default='')
    charged_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='charges')
    charged_for = models.CharField(
        max_length=20, choices=CHARGED_FOR_CHOICES)
    status = models.CharField(
        max_length=20, default='NEW', choices=CHARGE_STATUS_CHOICES)
    charge_status_context = models.CharField(
        max_length=20, default='', choices=CHARGE_STATUS_CONTEXT_CHOICES
    )
    pricing = models.OneToOneField(
        ChargePricing, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(null=True)
    expires_at = models.DateTimeField(null=True)
    # This flag will be set by the related task such as send email and
    # add coin to user in case of successful coin purchase
    charged_for_related_task_is_done = models.BooleanField(default=False)


class ChargePayment(models.Model):
    charge = models.ForeignKey(
        Charge, on_delete=models.CASCADE, related_name='payments')
    localamount = models.CharField(max_length=100, default='')
    localcurrency = models.CharField(max_length=100, default='USD')
    cryptoamount = models.CharField(max_length=100, default='')
    cryptocurrency = models.CharField(max_length=100, default='')
    txid = models.TextField()
