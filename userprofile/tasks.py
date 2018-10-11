from celery import shared_task

from userprofile.utils import send_two_factor_email


@shared_task
def task_send_two_factor_email(username, access_token, email_type):
    return send_two_factor_email(username, access_token, email_type)
