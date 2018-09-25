import os
import random

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User

from userprofile.models import (
    UserProfile, UserPhoto, UserDocument)


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
