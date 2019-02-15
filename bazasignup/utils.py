from datetime import timedelta

from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.conf import settings
from django.contrib.auth.models import User

from twilio.rest import Client

from bazasignup.models import (
    PhoneVerification,
    EmailVerification,
    BazaSignup,
    BazaSignupReferralCode
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
    email_verification, created = EmailVerification.objects.get_or_create(
        signup=signup
    )
    email_verification.email = email
    email_verification.verification_code = verification_code
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
    phone_verification, created = PhoneVerification.objects.get_or_create(
        signup=signup
    )
    phone_verification.verification_code = verification_code
    phone_verification.phone_number = phone_number
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


def get_unique_referral_code():
    referral_code = get_random_string(
        allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890',
        length=6
    )
    ref_code_exist = BazaSignupReferralCode.objects.filter(
        code=referral_code).exists()
    if ref_code_exist:
        return get_unique_referral_code()
    return referral_code


def process_after_approval(signup_id):
    system_user = User.objects.get(username='system')
    signup = BazaSignup.objects.get(id=signup_id)
    referral_code = get_unique_referral_code()
    bazasignupreferralcode, created = \
        BazaSignupReferralCode.objects.get_or_create(
            signup=signup
        )
    if created:
        bazasignupreferralcode.code = referral_code
        bazasignupreferralcode.save()
    email_template = loader.get_template('bazasignup/approval_mail.html')
    msg = EmailMultiAlternatives(
        'You are approved for Baza Distribution',
        'Your referral code is %s' % bazasignupreferralcode.code,
        'distsignup-noreply@baza.foundation',
        [signup.email])
    msg.attach_alternative(email_template.render({
        'referral_code': bazasignupreferralcode.code,
        'referral_url':
            'baza.foundation/profile/'
            '#!baza-signup?referral-code=%s' % bazasignupreferralcode.code
    }), "text/html")
    msg.send()
    signup.verified_date = now()
    signup.changed_by = system_user
    signup.save()
    return True