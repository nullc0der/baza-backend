import requests

from django.core.cache import cache
from django.conf import settings

from oauth2_provider.models import get_access_token_model

URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


def get_authhelper_client_token():
    if not cache.get('authhelper_client_token'):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            'grant_type': 'client_credentials'
        }
        res = requests.post(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL + '/o/token/',
            data=data,
            headers=headers,
            auth=(
                settings.CENTRAL_AUTH_INTROSPECT_CLIENT_ID,
                settings.CENTRAL_AUTH_INTROSPECT_CLIENT_SECRET
            )
        )
        if res.status_code == 200:
            content = res.json()
            expires_in = content['expires_in']
            cache.set('authhelper_client_token',
                      content['access_token'], expires_in)
    return cache.get('authhelper_client_token')


class AuthHelperClient(object):
    def __init__(self, url):
        self.url = url

    def login_user(self, username, password):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            'grant_type': 'password',
            'username': username,
            'password': password,
            'scope':
                'baza' if settings.SITE_TYPE == 'production' else 'baza-beta'
        }
        res = requests.post(
            self.url,
            headers=headers,
            data=data,
            auth=(
                settings.CENTRAL_AUTH_USER_LOGIN_CLIENT_ID,
                settings.CENTRAL_AUTH_USER_LOGIN_CLIENT_SECRET
            )
        )
        return res.status_code, res.json()

    def logout_user(self, token):
        AccessToken = get_access_token_model()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            'token': token,
            'token_type_hint': 'access_token'
        }
        res = requests.post(
            self.url,
            headers=headers,
            data=data,
            auth=(
                settings.CENTRAL_AUTH_USER_LOGIN_CLIENT_ID,
                settings.CENTRAL_AUTH_USER_LOGIN_CLIENT_SECRET
            )
        )
        if res.status_code == 200:
            try:
                AccessToken.objects.get(token=token).revoke()
            except AccessToken.DoesNotExist:
                pass
        return res.status_code

    def register_user(self, **kwargs):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token,
        }
        data = {
            'username': kwargs.pop('username'),
            'password': kwargs.pop('password'),
            'password1': kwargs.pop('password1'),
            'email': kwargs.pop('email'),
            'email_validation': settings.EMAIL_VERIFICATION,
            'initiator_site': settings.HOST_URL,
            'initiator_use_ssl':
            False if settings.SITE_TYPE == 'local' else True,
            'initiator_email': settings.INITIATOR_EMAIL
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def validate_email(self, validation_key):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'validation_key': validation_key
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def check_email_verified(self, token_to_check):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'token': token_to_check
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def initate_forgot_password_flow(self, email):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'email': email,
            'initiator_site': settings.HOST_URL,
            'initiator_use_ssl':
            False if settings.SITE_TYPE == 'local' else True,
            'initiator_email': settings.INITIATOR_EMAIL
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def reset_user_password(self, password, password1, reset_token):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'password': password,
            'password1': password1,
            'reset_token': reset_token
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def convert_social_user_token(self, token, backend):
        data = {
            'backend': backend,
            'token': token,
            'email_validation': settings.EMAIL_VERIFICATION,
            'initiator_site': settings.HOST_URL,
            'initiator_use_ssl':
            False if settings.SITE_TYPE == 'local' else True,
            'initiator_email': settings.INITIATOR_EMAIL,
            'client_id': settings.CENTRAL_AUTH_USER_LOGIN_CLIENT_ID,
            'client_secret': settings.CENTRAL_AUTH_USER_LOGIN_CLIENT_SECRET,
            'scope':
                'baza' if settings.SITE_TYPE == 'production' else 'baza-beta',
            'grant_type': 'convert_token'
        }
        res = requests.post(
            self.url,
            data=data
        )
        return res.status_code, res.json()

    def add_user_email(self, email, access_token):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'email': email,
            'access_token': access_token,
            'initiator_site': settings.HOST_URL,
            'initiator_use_ssl':
            False if settings.SITE_TYPE == 'local' else True,
            'initiator_email': settings.INITIATOR_EMAIL
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def get_twitter_request_code(self):
        callback_uris = {
            'local': 'http://localhost:5100/twicallback/',
            'production': 'https://baza.foundation/twicallback/',
            'development': 'https://beta.baza.foundation/twicallback/',
        }
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'callback_uri': callback_uris[settings.SITE_TYPE]
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def get_twitter_user_token(self, oauth_token, oauth_verifier):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'oauth_token': oauth_token,
            'oauth_verifier': oauth_verifier
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()
