import os
import random

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.utils.timezone import now

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from oauth2_provider.models import get_access_token_model

from userprofile.models import (
    UserProfile, UserPhoto, UserDocument, UserTasks,
    UserProfilePhoto
)
from userprofile.utils import get_user_tasks


AccessToken = get_access_token_model()


def delete_file(path):
    if os.path.isfile(path):
        os.remove(path)


@receiver(post_save, sender=User)
def create_user_profile(sender, **kwargs):
    instance = kwargs['instance']
    if kwargs['created']:
        colors = [
            '#c62828', '#7b1fa2', '#00838f',
            '#2e7d32', '#fbc02d', '#d84315'
        ]
        UserProfile.objects.create(
            user=instance,
            default_avatar_color=random.choice(colors))


@receiver(post_delete, sender=UserPhoto)
def remove_user_photo(sender, **kwargs):
    instance = kwargs['instance']
    if instance.photo:
        delete_file(instance.photo.path)


@receiver(post_delete, sender=UserDocument)
def remove_user_document(sender, **kwargs):
    instance = kwargs['instance']
    if instance.document:
        delete_file(instance.document.path)


# TODO: Research on updating last login
@receiver(post_save, sender=AccessToken)
def update_last_login(sender, **kwargs):
    instance = kwargs['instance']
    if kwargs['created']:
        user = instance.user
        user.last_login = now()
        user.save()


@receiver(post_save, sender=UserTasks)
def send_user_tasks(sender, **kwargs):
    instance = kwargs['instance']
    if not kwargs['created']:
        tasks = get_user_tasks(instance)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            '%s_tasks' % instance.user.username,
            {
                'type': 'userprofile.message',
                'message': tasks
            }
        )


@receiver(post_save)
def update_user_tasks(sender, **kwargs):
    instance = kwargs['instance']
    if sender.__name__ == 'UserProfile':
        if instance.location:
            usertasks = UserTasks.objects.get(user=instance.user)
            usertasks.added_location = True
            usertasks.save()
    if sender.__name__ == 'UserPhone':
        if instance.verified:
            usertasks = UserTasks.objects.get(user=instance.profile.user)
            usertasks.added_and_validated_phone = True
            usertasks.save()
    if sender.__name__ == 'UserTwoFactor':
        if instance.enabled:
            usertasks = UserTasks.objects.get(user=instance.user)
            usertasks.added_two_factor_authentication = True
            usertasks.save()
    if sender.__name__ == 'BazaSignup':
        if len(instance.get_completed_steps()) == 4:
            usertasks = UserTasks.objects.get(user=instance.user)
            usertasks.completed_distribution_signup = True
            usertasks.save()
    if sender.__name__ == 'UserProfilePhoto':
        profile = instance.profile
        if profile.profilephotos.filter(is_active=True):
            usertasks = UserTasks.objects.get(user=profile.user)
            usertasks.added_profile_picture = True
            usertasks.save()


@receiver(post_delete, sender=UserProfilePhoto)
def update_profile_picture_task(sender, **kwargs):
    instance = kwargs['instance']
    profile = instance.profile
    if not profile.profilephotos.filter(is_active=True):
        usertasks = UserTasks.objects.get(user=profile.user)
        usertasks.added_profile_picture = False
        usertasks.save()
