from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.gis.geoip2 import GeoIP2

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from iso3166 import countries

from coinbasepay.models import Charge
from donation.models import Donation
from donation.tasks import task_send_donation_confirm_email


STATUSES = ['CONFIRMED', 'UNRESOLVED']
channel_layer = get_channel_layer()


def get_total_price(payments):
    price = 0
    for payment in payments:
        if not payment.is_rewarded:
            price += float(payment.localamount)
            payment.is_rewarded = True
            payment.save()
    return price


def send_donation_stat(logged_ip):
    try:
        g = GeoIP2()
        city = g.city(logged_ip)
        async_to_sync(channel_layer.group_send)(
            'donations',
            {
                'type': 'donation.message',
                'message': {
                    'iso': countries.get(city['country_code'].lower()).alpha3
                }
            }
        )
    except:
        pass


@receiver(post_save, sender=Charge)
def finish_donation_process(sender, instance, created, **kwargs):
    if instance.charged_for == 'DONATION':
        if instance.status in STATUSES\
                and not instance.charged_for_related_task_is_done:
            price = get_total_price(instance.payments.all())
            if price != 0:
                donation = Donation.objects.get(
                    coinbase_charge=instance)
                donation.is_pending = False
                donation.amount = price
                instance.charged_for_related_task_is_done = True
                task_send_donation_confirm_email.delay(donation.id)
                donation.save()
                instance.save()
                if donation.logged_ip:
                    send_donation_stat(donation.logged_ip)
