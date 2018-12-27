from celery import shared_task

from coinbasepay.utils import resolve_charge


@shared_task
def task_resolve_charge(charge_id):
    return resolve_charge(charge_id)

# @shared_task
# def task_send_email_if_unresolved_charge(charge_id):
#     return send_email_if_unresolved_charge(charge_id)
