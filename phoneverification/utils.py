from datetime import timedelta

from django.conf import settings
from django.apps import apps
from django.utils.timezone import now
from django.utils.crypto import get_random_string
from django.contrib.contenttypes.models import ContentType

from twilio.rest import Client

from phoneverification.models import PhoneVerification


def send_phone_verification_code(
        related_obj_model_name, related_obj_id, phone_number=None):
    related_obj = apps.get_model(
        related_obj_model_name).objects.get(id=related_obj_id)
    related_obj_type = ContentType.objects.get_for_model(related_obj)
    try:
        phone_verification = PhoneVerification.objects.get(
            content_type__pk=related_obj_type.id, object_id=related_obj.id
        )
        created = False
    except PhoneVerification.DoesNotExist:
        phone_verification = PhoneVerification.objects.create(
            content_object=related_obj
        )
        created = True
    if created:
        phone_verification.phone_number = phone_number
        phone_verification.verification_code = get_random_string(
            length=6, allowed_chars='0123456789')
        phone_verification.sms_send_count += 1
    else:
        if phone_verification.created_on + timedelta(
                seconds=settings.PHONE_VERIFICATION_CODE_EXPIRES_IN) < now():
            phone_verification.verification_code = get_random_string(
                length=6, allowed_chars='0123456789')
            phone_verification.created_on = now()
            phone_verification.sms_send_count = 1
        else:
            phone_verification.sms_send_count += 1
        if phone_number:
            phone_verification.phone_number = phone_number
    phone_verification.save()
    if phone_verification.sms_send_count <= 3:
        message_body = "Use code %s to verify your phone" \
            % phone_verification.verification_code + \
            " number at baza foundation"
        client = Client(
            settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            to=phone_verification.phone_number,
            from_=settings.TWILIO_PHONE_NO
        )
        return message.status
    return "%s: USER ALREADY ASKED 3 TIMES TO" \
        % phone_verification.phone_number + " SEND SMS WITHIN EXPIRY TIME"
