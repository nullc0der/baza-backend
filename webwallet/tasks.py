from __future__ import absolute_import, unicode_literals

from celery import shared_task

from webwallet.utils import send_main_wallet_low_balance_email_to_admins


@shared_task
def task_send_main_wallet_low_balance_email_to_admins():
    return send_main_wallet_low_balance_email_to_admins()
