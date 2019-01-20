import os

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_delete


def user_directory(instance, filename):
    return 'userhashtagimage/user_{0}/{1}'.format(
        instance.user.id, filename)


class HashtagImage(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='hashtagimages')
    image = models.ImageField(upload_to=user_directory)
    uid = models.CharField(max_length=12, default='')


@receiver(post_delete, sender=HashtagImage)
def remove_user_hashtag_image(sender, **kwargs):
    instance = kwargs['instance']
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
