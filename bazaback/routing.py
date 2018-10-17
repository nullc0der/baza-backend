from django.urls import path

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from bazaback.tokenauth import TokenAuthMiddlewareStack
from notifications.consumers import NotificationConsumer
from publicusers.consumers import PublicusersConsumer
from messenger.consumers import MessengerConsumer


application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter([
                path('ws/notifications/', NotificationConsumer),
                path('ws/users/', PublicusersConsumer),
                path('ws/messenger/', MessengerConsumer)
            ])
        )
    )
})
