from django.contrib.auth.models import AnonymousUser

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


class NotificationConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.room_group_name = 'notifications_for_%s' % self.user.username
        if not isinstance(self.user, AnonymousUser):
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            # TODO: Change this to self.accept once find a solution for
            # Adding token header
            self.accept(self.scope['subprotocols'][0])
        else:
            self.close()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def notification_message(self, event):
        self.send_json({
            'message': event['message']
        })
