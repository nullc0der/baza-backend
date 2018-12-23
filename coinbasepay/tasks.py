from celery import shared_task

from coinbasepay.utils import send_email_if_unresolved_charge


@shared_task
def task_send_email_if_unresolved_charge(charge_id):
    return send_email_if_unresolved_charge(charge_id)
