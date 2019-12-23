from celery import shared_task

from bounty.utils import send_reward


@shared_task
def task_send_reward(user_id, task_name, can_have_multiple=False, amount=0):
    return send_reward(user_id, task_name, can_have_multiple, amount)
