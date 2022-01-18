from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser

from oauth2_provider.models import get_access_token_model


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        headers = dict(scope['headers'])
        # HACK: Websocket browser client don't supports header
        # at this moment. See https://stackoverflow.com/a/35890141
        # We will send token with sec-websocket-protocol
        # header from browser and parse here
        if b'sec-websocket-protocol' in headers:
            AccessToken = get_access_token_model()
            try:
                token_name, token_key = headers[
                    b'sec-websocket-protocol'].decode(
                ).split('-')
                print(token_name, token_key)
                if token_name == 'Bearer':
                    token = AccessToken.objects.get(token=token_key)
                    scope['user'] = token.user
                    print(scope['user'])
            except AccessToken.DoesNotExist:
                scope['user'] = AnonymousUser()
        return self.inner(scope)


def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(
        AuthMiddlewareStack(inner))
