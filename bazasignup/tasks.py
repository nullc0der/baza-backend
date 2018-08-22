from __future__ import absolute_import, unicode_literals

from celery import shared_task

from bazasignup.utils import (
    send_email_verfication_code,
    send_email_verfication_code_again
)


@shared_task
def task_send_email_verification_code(email, signup_id):
    return send_email_verfication_code(email, signup_id)


@shared_task
def task_send_email_verification_code_again(signup_id):
    return send_email_verfication_code_again(signup_id)
