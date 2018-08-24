from datetime import timedelta

from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.core.mail import EmailMultiAlternatives
from django.template import loader, Context
from django.conf import settings

from twilio.rest import Client

from bazasignup.models import (
    PhoneVerification,
    EmailVerification,
    BazaSignup
)


def send_email_verfication_code(email, signup_id):
    signup = BazaSignup.objects.get(id=signup_id)
    verification_code = get_random_string(length=6, allowed_chars='0123456789')
    email_template = loader.get_template('bazasignup/verification_code.html')
    msg = EmailMultiAlternatives(
        'Validate email for baza distribution signup',
        'Validate your email with code %s,'
        ' valid for 2 minute' % verification_code,
        'emailvalidation-noreply@baza.foundation',
        [email])
    msg.attach_alternative(email_template.render({
        'verification_code': verification_code
    }), "text/html")
    msg.send()
    email_verification = EmailVerification(
        email=email,
        signup=signup,
        verification_code=verification_code
    )
    email_verification.save()
    return True


def send_email_verfication_code_again(signup_id):
    signup = BazaSignup.objects.get(id=signup_id)
    email_verification, created = EmailVerification.objects.get_or_create(
        signup=signup
    )
    if email_verification.created_on + timedelta(seconds=120) < now():
        email_verification.verification_code = get_random_string(
            length=6, allowed_chars='0123456789')
    email_verification.created_on = now()
    email_verification.save()
    verification_code = email_verification.verification_code
    email_template = loader.get_template('bazasignup/verification_code.html')
    msg = EmailMultiAlternatives(
        'Validate email for baza distribution signup',
        'Validate your email with code %s,'
        ' valid for 2 minute' % verification_code,
        'emailvalidation-noreply@baza.foundation',
        [email_verification.email])
    msg.attach_alternative(email_template.render({
        'verification_code': verification_code
    }), "text/html")
    msg.send()
    return True


def send_phone_verification_code(signup_id, phone_number):
    signup = BazaSignup.objects.get(id=signup_id)
    verification_code = get_random_string(length=6, allowed_chars='0123456789')
    message_body = \
        "Use code %s for baza signup\n valid for 2 minute" % verification_code
    client = Client(
        settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message_body,
        to=phone_number,
        from_=settings.TWILIO_PHONE_NO
    )
    phone_verification = PhoneVerification(
        phone_number=phone_number,
        signup=signup,
        verification_code=verification_code
    )
    phone_verification.save()
    return message.status


def send_phone_verification_code_again(signup_id):
    signup = BazaSignup.objects.get(id=signup_id)
    phone_verification, created = PhoneVerification.objects.get_or_create(
        signup=signup
    )
    if phone_verification.created_on + timedelta(seconds=120) < now():
        phone_verification.verification_code = get_random_string(
            length=6, allowed_chars='0123456789')
    phone_verification.created_on = now()
    phone_verification.save()
    verification_code = phone_verification.verification_code
    message_body = \
        "Use code %s for baza signup\n valid for 2 minute" % verification_code
    client = Client(
        settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message_body,
        to=phone_verification.phone_number,
        from_=settings.TWILIO_PHONE_NO
    )
    return message.status
