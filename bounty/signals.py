from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from donation.models import Donation

from bounty.tasks import task_send_reward
from bounty.bounties import BAZA_BAZ_BOUNTY_2


@receiver(post_save, sender=User)
def send_signup_reward_to_user(sender, **kwargs):
    instance = kwargs['instance']
    bounty_task_name = BAZA_BAZ_BOUNTY_2['tasks']['signed_up']['name']
    if kwargs['created']:
        task_send_reward.delay(instance.id, bounty_task_name)


@receiver(post_save, sender=Donation)
def send_reward_to_donation_referrer(sender, **kwargs):
    instance = kwargs['instance']
    bounty_task_name = BAZA_BAZ_BOUNTY_2['tasks']['donation_referral']['name']
    if kwargs['created'] and instance.user:
        donor = instance.user
        if hasattr(donor, 'bazasignup'):
            if donor.bazasignup.is_donor and donor.bazasignup.referred_by\
                    and donor.bazasignup.status == 'approved':
                task_send_reward.delay(
                    donor.bazasignup.referred_by.id,
                    bounty_task_name,
                    can_have_multiple=True,
                    amount=instance.amount * 10
                )
