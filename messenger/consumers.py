from django.contrib.auth.models import AnonymousUser

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from messenger.models import ChatRoom


class MessengerConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.room_group_name = '%s_messages' % self.user.username
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

    def receive_json(self, content):
        try:
            chatroom = ChatRoom.objects.get(id=content.get('chatroom_id'))
            if self.user in chatroom.subscribers.all():
                otherusers = []
                for user in chatroom.subscribers.all():
                    if self.user != user:
                        otherusers.append(user)
                for otheruser in otherusers:
                    message_dict = {
                        'chatroom_id': chatroom.id,
                        'type': 'set_typing'
                    }
                    async_to_sync(self.channel_layer.group_send)(
                        '%s_messages' % otheruser.username,
                        {
                            'type': 'messenger.message',
                            'message': message_dict
                        }
                    )
        except ChatRoom.DoesNotExist:
            pass

    def messenger_message(self, event):
        self.send_json({
            'message': event['message']
        })
