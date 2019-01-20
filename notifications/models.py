from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


# Create your models here.


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='usernotifications')
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
