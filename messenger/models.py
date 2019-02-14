import os

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.conf import settings

# Create your models here.


class ChatRoom(models.Model):
    name = models.CharField(max_length=200, unique=True)
    subscribers = models.ManyToManyField(User)
    unsubscribers = models.ManyToManyField(
        User, related_name='unsubscribed_rooms')
    date_created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __unicode__(self):
        return "%s" % self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    to_user = models.ForeignKey(
        User,
        related_name='recieved_messages',
        null=True,
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(
        ChatRoom, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    attachment_type = models.CharField(max_length=40, default='')
    attachment_path = models.CharField(max_length=200, default='')
    read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(Message, self).save(*args, **kwargs)
        self.room.save()


def delete_attachment(sender, instance, **kwargs):
    if instance.attachment_path:
        file_path = os.path.join(
            settings.MEDIA_ROOT, 'messenger',
            instance.room.name, instance.attachment_path.split('/')[-1])
        if os.path.exists(file_path):
            os.remove(file_path)


pre_delete.connect(delete_attachment, sender=Message)
