import base64
import logging
from datetime import datetime, timedelta

import requests
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware
from oauth2_provider.validators import Oauth2Validator
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.models import get_access_token_model

log = logging.getLogger("oauth2_provider")
UserModel = get_user_model()
AccessToken = get_access_token_model()


class NewOauth2Validator(Oauth2Validator):
    def _get_token_from_authentication_server(
            self, token, introspection_url, introspection_token,
            introspection_credentials
    ):
        """Use external introspection endpoint to "crack open" the token.
        :param introspection_url: introspection endpoint URL
        :param introspection_token: Bearer token
        :param introspection_credentials: Basic Auth credentials (id,secret)
        :return: :class:`models.AccessToken`
        Some RFC 7662 implementations (including this one) use a Bearer token
        while others use Basic Auth. Depending on the external
        AS's implementation, provide either the introspection_token or
        the introspection_credentials. If the resulting access_token identifies
        a username (e.g. Authorization Code grant), add that user to the
        UserModel. Also cache the access_token up until its expiry time
        or a configured maximum time.
        """
        headers = None
        if introspection_token:
            headers = {"Authorization": "Bearer {}".format(
                introspection_token)}
        elif introspection_credentials:
            client_id = introspection_credentials[0].encode("utf-8")
            client_secret = introspection_credentials[1].encode("utf-8")
            basic_auth = base64.b64encode(client_id + b":" + client_secret)
            headers = {"Authorization": "Basic {}".format(
                basic_auth.decode("utf-8"))}

        try:
            response = requests.post(
                introspection_url,
                data={"token": token}, headers=headers
            )
        except requests.exceptions.RequestException:
            log.exception(
                "Introspection: Failed POST to %r in token lookup",
                introspection_url)
            return None

        try:
            content = response.json()
        except ValueError:
            log.exception("Introspection: Failed to parse response as json")
            return None

        if "active" in content and content["active"] is True:
            if "username" in content:
                user, _created = UserModel.objects.get_or_create(
                    **{UserModel.USERNAME_FIELD: content["username"]}
                )
            else:
                user = None

            max_caching_time = datetime.now() + timedelta(
                seconds=oauth2_settings.RESOURCE_SERVER_TOKEN_CACHING_SECONDS
            )

            if "exp" in content:
                expires = datetime.utcfromtimestamp(content["exp"])
                if expires > max_caching_time:
                    expires = max_caching_time
            else:
                expires = max_caching_time

            scope = content.get("scope", "")
            expires = make_aware(expires)

            access_token, _created = AccessToken\
                .objects.select_related("application", "user")\
                .update_or_create(token=token,
                                  defaults={
                                      "user": user,
                                      "application": None,
                                      "scope": scope,
                                      "expires": expires,
                                  })

            return access_token
