from django.urls import path, include

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from bazaback.tokenauth import TokenAuthMiddlewareStack
from notifications.consumers import NotificationConsumer


application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter([
                path(
                    'ws/notifications/', NotificationConsumer)
            ])
        )
    )
})
