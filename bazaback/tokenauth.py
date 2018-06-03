from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser


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
            try:
                token_name, token_key = headers[
                    b'sec-websocket-protocol'].decode(
                ).split('-')
                if token_name == 'Token':
                    token = Token.objects.get(key=token_key)
                    scope['user'] = token.user
            except Token.DoesNotExist:
                scope['user'] = AnonymousUser()
        return self.inner(scope)


def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(
        AuthMiddlewareStack(inner))
