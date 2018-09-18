from celery import shared_task

from taigaissuecreator.utils import post_issue


@shared_task
def task_post_issue(posted_by_id, subject, description, attachments_ids):
    return post_issue(posted_by_id, subject, description, attachments_ids)
