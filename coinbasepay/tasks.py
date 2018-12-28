from celery import shared_task

from coinbasepay.utils import resolve_charge


@shared_task
def task_resolve_charge(charge_id):
    return resolve_charge(charge_id)
