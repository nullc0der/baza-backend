from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from userprofile.signals import delete_file

from bazasignup.models import BazaSignup
from bazasignup.tasks import task_process_after_approval


@receiver(post_save, sender=BazaSignup)
def process_post_approval(sender, **kwargs):
    signup = kwargs['instance']
    if signup.status == 'approved' and not signup.verified_date:
        task_process_after_approval.delay(signup.id)


@receiver(post_delete, sender=BazaSignup)
def delete_signup_image(sender, **kwargs):
    signup = kwargs['instance']
    if signup.photo:
        delete_file(signup.photo.path)
