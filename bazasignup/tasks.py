from __future__ import absolute_import, unicode_literals

from celery import shared_task

from bazasignup.utils import (
    send_email_verfication_code,
    send_email_verfication_code_again,
    send_phone_verification_code,
    send_phone_verification_code_again,
    process_after_approval,
    send_invalidation_email_to_user,
    post_resubmission
)

from bazasignup.autoapproval import BazaSignupAutoApproval


@shared_task
def task_send_email_verification_code(email, signup_id):
    return send_email_verfication_code(email, signup_id)


@shared_task
def task_send_email_verification_code_again(signup_id):
    return send_email_verfication_code_again(signup_id)


@shared_task
def task_send_phone_verification_code(signup_id, phone_number):
    return send_phone_verification_code(signup_id, phone_number)


@shared_task
def task_send_phone_verification_code_again(signup_id):
    return send_phone_verification_code_again(signup_id)


@shared_task
def task_process_autoapproval(signup_id):
    return BazaSignupAutoApproval(signup_id).start()


@shared_task
def task_process_after_approval(signup_id):
    return process_after_approval(signup_id)


@shared_task
def task_send_invalidation_email_to_user(signup_id):
    return send_invalidation_email_to_user(signup_id)


@shared_task
def task_post_resubmission(signup_id):
    return post_resubmission(signup_id)
