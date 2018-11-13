from celery import task, shared_task

from group.utils import (
    process_flagged_for_delete_group, create_notification)


@task
def task_process_flagged_for_delete_group():
    return process_flagged_for_delete_group()


@shared_task
def task_create_notification(objid, objtype, basicgroupid):
    return create_notification(objid, objtype, basicgroupid)
