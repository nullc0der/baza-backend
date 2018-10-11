from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from authclient.utils import AuthHelperClient

URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


def send_two_factor_email(username, access_token, email_type):
    EMAIL_TEMPLATES = {
        0: 'userprofile/twofactorenabled.html',
        1: 'userprofile/twofactordisabled.html',
        2: 'userprofile/recoverycodedownloaded.html'
    }
    authhelperclient = AuthHelperClient(
        URL_PROTOCOL +
        settings.CENTRAL_AUTH_INTROSPECT_URL +
        '/authhelper/useremails/'
    )
    res_status, data = authhelperclient.get_user_emails(access_token)
    if res_status == 200:
        primary_emails = [
            email for email in data if email['primary'] and email['verified']]
        if len(primary_emails):
            email_template = loader.get_template(EMAIL_TEMPLATES[email_type])
            msg = EmailMultiAlternatives(
                subject='Account Alert',
                body='Two Factor Notification',
                from_email='system-noreply@baza.foundation',
                to=[primary_emails[0]['email']]
            )
            msg.attach_alternative(email_template.render({
                'username': username
            }), 'text/html')
            msg.send()
