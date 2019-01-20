from celery import shared_task

from coinpurchase.utils import create_proxc_transaction


@shared_task
def task_create_proxc_transaction(coinpurchase_id):
    return create_proxc_transaction(coinpurchase_id)
