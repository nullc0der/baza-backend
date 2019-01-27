from django.contrib.auth.models import AnonymousUser

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


class DonationConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.room_group_name = 'donations'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        # TODO: Change this to self.accept once find a solution for
        # Adding token header
        if not isinstance(self.user, AnonymousUser):
            self.accept(self.scope['subprotocols'][0])
        else:
            self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def donation_message(self, event):
        self.send_json({
            'message': event['message']
        })
