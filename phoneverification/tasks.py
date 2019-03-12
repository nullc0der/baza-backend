from celery import shared_task

from phoneverification.utils import send_phone_verification_code


@shared_task
def task_send_phone_verification_code(
        related_obj_model_name, related_obj_id, phone_number):
    return send_phone_verification_code(
        related_obj_model_name, related_obj_id, phone_number)
