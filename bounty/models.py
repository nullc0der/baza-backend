from django.db import models
from django.contrib.auth.models import User


class BountyProgram(models.Model):
    name = models.CharField(default='', max_length=200)
    total_amount = models.PositiveIntegerField()
    rewarded_amount = models.PositiveIntegerField(default=0)
    enabled_for_site = models.BooleanField(default=False)
    valid_till = models.DateTimeField()

    def __str__(self):
        return self.name


class RewardedBounty(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='rewarded_bounties')
    bounty_program = models.ForeignKey(
        BountyProgram, on_delete=models.SET_NULL, null=True,
        related_name='rewarded_users')
    rewarded_for_task = models.CharField(default='', max_length=200)
    amount = models.PositiveIntegerField()
