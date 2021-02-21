import requests

from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from landingcontact.models import LandingContact


def send_email_to_site_owner(contact_id):
    landingcontact = LandingContact.objects.get(
        id=contact_id
    )
    email_template = loader.get_template('landingcontact/owner_email.html')
    for email_id in settings.SITE_OWNER_EMAILS:
        msg = EmailMultiAlternatives(
            subject='New contact message recieved',
            body='Name: %s\nEmail: %s\nOriginal subject: %s\nMessage: %s\nSent at: %s' % (
                landingcontact.name,
                landingcontact.email,
                landingcontact.subject,
                landingcontact.message,
                landingcontact.timestamp
            ),
            from_email='system-noreply@baza.foundation',
            to=email_id
        )
        msg.attach_alternative(
            email_template.render({
                'name': landingcontact.name,
                'email': landingcontact.email,
                'original_subject': landingcontact.subject,
                'message': landingcontact.message,
                'timestamp': landingcontact.timestamp
            }),
            'text/html'
        )
        msg.send()


def get_recaptcha_response(token):
    data = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': token
    }
    res = requests.post(
        'https://www.google.com/recaptcha/api/siteverify', data)
    if res.status_code == 200:
        return res.json()
    return
