from celery import shared_task

from landingcontact.utils import send_email_to_site_owner


@shared_task
def task_send_email_to_site_owner(contact_id):
    return send_email_to_site_owner(contact_id)
