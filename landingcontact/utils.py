from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from landingcontact.models import LandingContact


def send_email_to_site_owner(contact_id):
    landingcontact = LandingContact.objects.get(
        id=contact_id
    )
    email_template = loader.get_template('landingcontact/owner_email.html')
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
        to=settings.SITE_OWNER_EMAILS.split(',')
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
