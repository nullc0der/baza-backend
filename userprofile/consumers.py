from django.contrib.auth.models import AnonymousUser

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from userprofile.tasks import task_compute_user_tasks


class UserProfileConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.room_group_name = '%s_tasks' % self.user.username
        if not isinstance(self.user, AnonymousUser):
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            # TODO: Change this to self.accept once find a solution for
            # Adding token header
            self.accept(self.scope['subprotocols'][0])
            task_compute_user_tasks.delay(
                self.user.id, self.scope['subprotocols'][0].split('-')[1])
        else:
            self.close()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def userprofile_message(self, event):
        self.send_json({
            'message': event['message']
        })
