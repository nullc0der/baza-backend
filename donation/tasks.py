from celery import shared_task

from donation.utils import send_donation_confirm_email


@shared_task
def task_send_donation_confirm_email(donation_id):
    return send_donation_confirm_email(donation_id)
