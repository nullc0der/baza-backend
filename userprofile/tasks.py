from celery import shared_task

from userprofile.utils import (
    send_two_factor_email, send_phone_verification_code, compute_user_tasks,
    add_baza_invitation_reward
)


@shared_task
def task_send_two_factor_email(username, access_token, email_type):
    return send_two_factor_email(username, access_token, email_type)


@shared_task
def task_send_phone_verification_code(phone_number):
    return send_phone_verification_code(phone_number)


@shared_task
def task_compute_user_tasks(user_id, access_token):
    return compute_user_tasks(user_id, access_token)


@shared_task
def task_add_baza_invitation_reward(username: str):
    return add_baza_invitation_reward(username)
