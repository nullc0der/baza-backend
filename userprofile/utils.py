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


def user_has_verified_email(access_token):
    authhelperclient = AuthHelperClient(
        URL_PROTOCOL +
        settings.CENTRAL_AUTH_INTROSPECT_URL +
        '/authhelper/useremails/'
    )
    res_status, data = authhelperclient.get_user_emails(access_token)
    if res_status == 200:
        primary_emails = [
            email for email in data if email['primary'] and email['verified']]
        return bool(len(primary_emails))
    return False


def user_has_two_factor(user):
    if hasattr(user, 'two_factor'):
        return user.two_factor.enabled
    return False


def user_has_social_account_linked(access_token):
    authhelperclient = AuthHelperClient(
        URL_PROTOCOL +
        settings.CENTRAL_AUTH_INTROSPECT_URL +
        '/authhelper/getsocialauths/'
    )
    res_status, data = authhelperclient.get_user_social_auths(access_token)
    if res_status == 200:
        return bool(len(data))
    return False


def user_has_completed_distribution_signup(user):
    if hasattr(user, 'bazasignup'):
        signup = user.bazasignup
        # completed_steps = list(
        #     map(lambda x: int(x), signup.get_completed_steps()))
        # not_completed_steps = []
        # for i in range(4):
        #     if i not in completed_steps:
        #         not_completed_steps.append(i)
        return bool(len(signup.get_completed_steps()) == 4)
    return False


def get_user_tasks(user, access_token):
    # TODO: Make this a task and trigger the task in login method
    # and on API call just return db stored values
    verified_email = user_has_verified_email(access_token)
    location = user.profile.location
    two_factor = user_has_two_factor(user)
    social_account_linked = user_has_social_account_linked(
        access_token)
    completed_distribution_signup = user_has_completed_distribution_signup(
        user)
    tasks = [
        {
            'status': 'done' if verified_email else 'pending',
            'href': '#details',
            'id': 1,
            'description': 'Add an email id and verify'
        },
        {
            'status': 'done' if location else 'pending',
            'href': '#profile',
            'id': 2,
            'description': 'Add your location'
        },
        {
            'status': 'done' if two_factor else 'pending',
            'href': '#security',
            'id': 3,
            'description': 'Enable two factor'
        },
        {
            'status': 'done' if social_account_linked else 'pending',
            'href': '#details',
            'id': 4,
            'description': 'Link a social account'
        },
        {
            'status': 'done' if completed_distribution_signup else 'pending',
            'href': '#!baza-signup',
            'id': 5,
            'description': 'Complete distribution signup'
        }
    ]
    trust_percentage = 0
    trust_percentage += 10 if completed_distribution_signup else 0
    trust_percentage += 10 if verified_email else 0
    trust_percentage += 10 if location else 0
    trust_percentage += 10 if two_factor else 0
    trust_percentage += 10 if social_account_linked else 0
    return {
        'tasks': tasks,
        'trust_percentage': trust_percentage
    }
