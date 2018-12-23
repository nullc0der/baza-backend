from django.db.models.signals import post_save
from django.dispatch import receiver

from coinbasepay.models import Charge
from coinbasepay.tasks import task_send_email_if_unresolved_charge


@receiver(post_save, sender=Charge)
def send_email_for_unresolved_charge(sender, instance, created, **kwargs):
    if instance.status == 'UNRESOLVED':
        task_send_email_if_unresolved_charge.delay(instance.id)
