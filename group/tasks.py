from celery import task

from groupsystem.utils import process_flagged_for_delete_group


@task
def task_process_flagged_for_delete_group():
    return process_flagged_for_delete_group()
