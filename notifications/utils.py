from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from group.models import GroupInvite
from publicusers.views import make_user_serializeable
from bazasignup.models import BazaSignup

from notifications.models import Notification

channel_layer = get_channel_layer()


def get_serialized_notification(notification):
    data = {}
    if hasattr(notification, 'content_object'):
        if notification.content_object:
            if isinstance(notification.content_object, GroupInvite):
                groupinvite = notification.content_object
                data['type'] = 'groupinvite'
                data['inviteid'] = groupinvite.id
                data['id'] = notification.id
                data['sender'] = make_user_serializeable(groupinvite.sender)
                data['groupname'] = groupinvite.basic_group.name
            if isinstance(notification.content_object, BazaSignup):
                signup = notification.content_object
                data['type'] = 'distribution_signup'
                data['id'] = notification.id
                data['signupuser'] = make_user_serializeable(signup.user)
    return data


def create_user_notification(user, obj):
    notification = Notification(user=user, content_object=obj)
    notification.save()
    websocket_message = {
        'type': 'general',
        'data': get_serialized_notification(notification)
    }
    async_to_sync(channel_layer.group_send)(
        'notifications_for_%s' % user.username,
        {
            'type': 'notification.message',
            'message': websocket_message
        }
    )
