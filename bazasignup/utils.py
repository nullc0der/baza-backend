from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.core.mail import EmailMultiAlternatives
from django.template import loader, Context

from bazasignup.models import EmailVerification, BazaSignup


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
    email_verification.created_on = now()
    email_verification.save()
    verification_code = email_verification.verification_code
    email_template = loader.get_template('bazasignup/verification_code.html')
    msg = EmailMultiAlternatives(
        'Validate email for baza distrubution signup',
        'Validate your email with code %s,'
        ' valid for 2 minute' % verification_code,
        'emailvalidation-noreply@baza.foundation',
        [email_verification.email])
    msg.attach_alternative(email_template.render({
        'verification_code': verification_code
    }), "text/html")
    msg.send()
    return True
