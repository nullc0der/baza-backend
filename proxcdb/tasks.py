from celery import task

from proxcdb.utils import send_per_minute_distribution


@task
def task_send_per_minute_distribution():
    return send_per_minute_distribution()
