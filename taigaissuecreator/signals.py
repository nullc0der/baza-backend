from django.dispatch import receiver
from django.db.models.signals import post_delete

from userprofile.signals import delete_file
from taigaissuecreator.models import TaigaIssueAttachment


@receiver(post_delete, sender=TaigaIssueAttachment)
def delete_signup_image(sender, **kwargs):
    issue_attachment = kwargs['instance']
    if issue_attachment.attachment:
        delete_file(issue_attachment.attachment.path)
