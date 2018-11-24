from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


class PublicusersConsumer(JsonWebsocketConsumer):

    def get_online_users(self):
        return cache.get('online_users')

    def set_online_users(self, user_id, status):
        data = {
            'id': user_id,
            'status': status
        }
        online_users = cache.get('online_users')
        for online_user in online_users:
            if online_user['id'] == user_id:
                online_users.remove(online_user)
        online_users.append(data)
        cache.set('online_users', online_users, None)

    def delete_online_users(self, user_id):
        online_users = cache.get('online_users')
        for online_user in online_users:
            if online_user['id'] == user_id:
                online_users.remove(online_user)
        cache.set('online_users', online_users, None)

    def broadcast_user_availability(self):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'onlineusers.message',
                'message': {
                    'online_users': list(self.get_online_users())
                }
            }
        )

    def connect(self):
        self.user = self.scope['user']
        self.room_group_name = 'online_users'
        if not isinstance(self.user, AnonymousUser):
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            # TODO: Change this to self.accept once find a solution for
            # Adding token header
            self.accept(self.scope['subprotocols'][0])
            self.set_online_users(self.user.id, 'online')
            self.broadcast_user_availability()
        else:
            self.close()

    def disconnect(self, code):
        self.delete_online_users(self.user.id)
        self.broadcast_user_availability()
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive_json(self, content):
        status = 'online'
        accepted_status = ['online', 'away', 'busy', 'idle']
        if content['status'] in accepted_status:
            status = content['status']
        self.set_online_users(self.user.id, status)
        self.broadcast_user_availability()

    def onlineusers_message(self, event):
        self.send_json({
            'message': event['message']
        })
