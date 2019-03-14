from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class PhoneVerification(models.Model):
    phone_number = models.CharField(max_length=15)
    verification_code = models.CharField(max_length=6)
    created_on = models.DateTimeField(auto_now_add=True)
    sms_send_count = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
