import os
import json
from itertools import groupby
from operator import itemgetter

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


def save_user_auth_data(data):
    user_auths = cache.get('user_auths')
    user_auths[data['uuid']] = data
    cache.set('user_auths', user_auths, None)


def get_user_auth_data(uuid):
    user_auths = cache.get('user_auths')
    try:
        return user_auths[uuid]
    except KeyError:
        return False


def delete_user_auth_data(uuid):
    user_auths = cache.get('user_auths')
    if uuid in user_auths:
        user_auths.pop(uuid)
        cache.set('user_auths', user_auths, None)


def save_disposable_email_domain_list() -> bool:
    disposable_email_domains_dir = settings.BASE_DIR + \
        '/authclient/datas/disposable_email_domains'
    if not os.path.isdir(disposable_email_domains_dir):
        os.makedirs(disposable_email_domains_dir)
    res = requests.get(
        'https://raw.githubusercontent.com/ivolo/' +
        'disposable-email-domains/master/index.json')
    if res.status_code == 200:
        splitted_domains = groupby(res.json(), key=itemgetter(0))
        for char, domains in splitted_domains:
            f = open(
                '{}/disposable_email_domains_{}.json'.format(
                    os.path.join(
                        settings.BASE_DIR,
                        'authclient/datas/disposable_email_domains'
                    ),
                    char
                ),
                'w+'
            )
            f.write(json.dumps(list(domains)))
        return True
    return False


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
            'scope': [
                'baza' if settings.SITE_TYPE == 'production' else 'baza-beta'
            ]
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
            'scope': [
                'baza' if settings.SITE_TYPE == 'production' else 'baza-beta'],
            'grant_type': 'convert_token'
        }
        res = requests.post(
            self.url,
            data=data
        )
        return res.status_code, res.json()

    def add_user_email(
            self, email, access_token, from_social=True, email_type='office'):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'email': email,
            'email_type': email_type,
            'access_token': access_token,
            'initiator_site': settings.HOST_URL,
            'initiator_use_ssl':
            False if settings.SITE_TYPE == 'local' else True,
            'initiator_email': settings.INITIATOR_EMAIL,
            'from_social': from_social
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def get_twitter_request_code(self):
        callback_uris = {
            'local': 'http://localhost:5100/twicallback/',
            'production': 'https://baza.foundation/twicallback/',
            'development': 'https://beta.baza.foundation/twicallback/',
            'apiserver': 'https://baza-demo.herokuapp.com/twicallback/'
        }
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'initiator_site': settings.HOST_URL,
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
            'initiator_site': settings.HOST_URL,
            'oauth_token': oauth_token,
            'oauth_verifier': oauth_verifier
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def update_user_special_scope(self, update_type, scope, username):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'update_type': update_type,
            'scope': scope,
            'username': username
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code

    def get_user_emails(self, access_token):
        """
        TIP: You can send username instead of access token if accessing
        username is not possible
        """
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'access_token': access_token
        }
        res = requests.get(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def get_user_primary_email(self, access_token):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'access_token': access_token
        }
        res = requests.get(self.url, headers=headers, data=data)
        if res.status_code == 200:
            primary_email = [
                email for email in res.json()
                if email['primary'] and email['verified']]
            if len(primary_email):
                return primary_email[0]['email']
        return

    def delete_user_email(self, access_token, email_id):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'access_token': access_token,
            'email_id': email_id
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def update_user_email(self, access_token, email_id, primary, email_type):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'access_token': access_token,
            'email_id': email_id,
            'primary': primary,
            'email_type': email_type
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def get_user_social_auths(self, access_token):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'access_token': access_token
        }
        res = requests.get(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def connect_social_auth(self, access_token, provider, **kwargs):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'access_token': access_token,
            'initiator_site': settings.HOST_URL,
            'provider': provider
        }
        if provider == 'twitter':
            data['oauth_token'] = kwargs['oauth_token']
            data['oauth_token_secret'] = kwargs['oauth_token_secret']
        else:
            data['provider_access_token'] = kwargs['provider_access_token']
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def disconnect_social_auth(self, access_token, provider, association_id):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'access_token': access_token,
            'provider': provider,
            'association_id': association_id
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def set_user_password(self, access_token, **kwargs):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'access_token': access_token,
            'current_password': kwargs['current_password'],
            'new_password_1': kwargs['new_password_1'],
            'new_password_2': kwargs['new_password_2']
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def check_user_password(self, access_token, password):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'access_token': access_token,
            'password': password
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def resend_email_validation(self, email):
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

    def check_user_has_usable_password(self, access_token):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'access_token': access_token
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def get_user_social_profile_photo(self, access_token, provider):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'access_token': access_token,
            'provider': provider
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def get_user_social_credentials(self, access_token, provider):
        token = get_authhelper_client_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        data = {
            'access_token': access_token,
            'provider': provider
        }
        res = requests.post(self.url, headers=headers, data=data)
        return res.status_code, res.json()

    def check_invited_to_baza(self, username: str) -> bool:
        res = requests.get(
            self.url,
            headers={
                "Authorization": f"Bearer {get_authhelper_client_token()}"
            },
            data={'username': username}
        )
        if res.status_code == 200:
            return res.json()['invited']
        return False
