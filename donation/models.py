from django.db import models
from django.contrib.auth.models import User

from stripepayment.models import Payment

# Create your models here.


class Donation(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='donations', null=True)
    amount = models.FloatField()
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_no = models.CharField(max_length=20, default='')
    stripe_payment = models.OneToOneField(
        Payment, on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return self.name
