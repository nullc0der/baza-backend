from __future__ import absolute_import, unicode_literals

from celery import task

from authclient.utils import save_disposable_email_domain_list


@task
def task_save_disposable_email_domain_list():
    return save_disposable_email_domain_list()
