from django.urls import path

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from bazaback.tokenauth import TokenAuthMiddlewareStack
from notifications.consumers import NotificationConsumer
from publicusers.consumers import PublicusersConsumer
from messenger.consumers import MessengerConsumer
from group.consumers import GroupConsumer
from userprofile.consumers import UserProfileConsumer
from donation.consumers import DonationConsumer

# NOTE: AllowedHostsOriginValidator is removed because it was failing to get
# HOST header, need to do research on it because it is not recommended to remove
application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter([
            path('ws/notifications/', NotificationConsumer),
            path('ws/users/', PublicusersConsumer),
            path('ws/messenger/', MessengerConsumer),
            path('ws/groupnotifications/', GroupConsumer),
            path('ws/profiletasks/', UserProfileConsumer),
            path('ws/donation/', DonationConsumer)
        ])
    )
})
