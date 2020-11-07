from celery import task

from proxcdb.utils import send_daily_distribution


@task
def task_send_daily_distribution():
    return send_daily_distribution()
