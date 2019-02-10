import base64
import logging
from datetime import datetime, timedelta

import requests
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware
from django.db.utils import IntegrityError
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.models import get_access_token_model

log = logging.getLogger("oauth2_provider")
UserModel = get_user_model()
AccessToken = get_access_token_model()


class NewOAuth2Validator(OAuth2Validator):
    def _get_token_from_authentication_server(
        self, token, introspection_url, introspection_token,
        introspection_credentials
    ):
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

            try:
                access_token = AccessToken.objects.select_related(
                    "application", "user").get(token=token)
            except AccessToken.DoesNotExist:
                try:
                    access_token = AccessToken.objects.create(
                        token=token,
                        user=user,
                        application=None,
                        scope=scope,
                        expires=expires
                    )
                # HACK: Kind of, the above code causes integrity error
                # when some simultaneous request comes from frontend and if the
                # access_token doesn't exist in db, as a side-affect frontend
                # results blank screen due to lack of 'profile' object, so as
                # a temporary solution I catched the IntegrityError
                except IntegrityError:
                    pass
            else:
                access_token.expires = expires
                access_token.scope = scope
                access_token.save()

            return access_token
