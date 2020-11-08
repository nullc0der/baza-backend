import os
from mimetypes import MimeTypes

from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from rest_framework import status, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from userprofile.utils import get_profile_photo

from messenger.permissions import IsChatRoomSubscriber
from messenger.serializers import ChatRoomSerializer, MessageSerializer
from messenger.models import ChatRoom, Message

channel_layer = get_channel_layer()


def _make_message_serializable(message):
    data = {}
    user = {
        'id': message.user.id,
        'username': message.user.profile.username or message.user.username,
        'user_image_url': get_profile_photo(message.user),
        'user_avatar_color': message.user.profile.default_avatar_color,
    }
    to_user = {
        'id': message.to_user.id,
        'username': message.to_user.profile.username
        or message.to_user.username,
        'user_image_url': get_profile_photo(message.to_user),
        'user_avatar_color': message.to_user.profile.default_avatar_color,
    }
    data["message"] = message.content
    data["timestamp"] = message.timestamp
    data["read"] = message.read
    data["to_user"] = to_user
    data["user"] = user
    data["id"] = message.id
    data["fileurl"] = message.attachment_path
    data["filetype"] = message.attachment_type
    data["filename"] = message.attachment_path.split('/')[-1]
    return data


def _make_chatroom_serializable(request, chat, for_ws=False):
    data = {}
    if not for_ws:
        otheruser = [user for user in chat.subscribers.all()
                     if user != request.user] or [
            user for user in chat.unsubscribers.all()
            if user != request.user]
    else:
        otheruser = [request.user]
        ws_user = [user for user in chat.subscribers.all()
                   if user != request.user] or [
            user for user in chat.unsubscribers.all()
            if user != request.user]
    if otheruser:
        data["id"] = chat.id
        data["unread_count"] = \
            chat.messages.filter(read=False).exclude(
                user=request.user).count() if not for_ws else\
            chat.messages.filter(read=False).exclude(user=ws_user[0]).count()
        data['user'] = {
            'id': otheruser[0].id,
            'username': otheruser[0].profile.username
            or otheruser[0].username,
            'user_image_url': get_profile_photo(otheruser[0]),
            'user_avatar_color':
                otheruser[0].profile.default_avatar_color
        }
    return data


class ChatRoomsView(APIView):
    """
    View to return all available chat rooms for an user

    * Only logged in user will be able to access this view
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        """
        Returns a list of available chat rooms
        """
        chats = ChatRoom.objects.filter(
            subscribers=request.user
        ).order_by('-updated')
        if chats:
            datas = []
            for chat in chats:
                data = _make_chatroom_serializable(request, chat)
                datas.append(data)
            serializer = ChatRoomSerializer(datas, many=True)
            return Response(serializer.data)
        return Response([])

    def post(self, request, to_user, format=None):
        user = User.objects.get(id=to_user)
        label = request.user.username + user.username
        label1 = user.username + request.user.username
        try:
            room1 = ChatRoom.objects.get(name=label)
        except ChatRoom.DoesNotExist:
            room1 = None
        try:
            room2 = ChatRoom.objects.get(name=label1)
        except ChatRoom.DoesNotExist:
            room2 = None
        if room1 or room2:
            if room1:
                chat = room1
            else:
                chat = room2
            if request.user in chat.unsubscribers.all():
                chat.unsubscribers.remove(request.user)
                chat.subscribers.add(request.user)
        else:
            chat, created = ChatRoom.objects.get_or_create(name=label)
            if created:
                chat.subscribers.add(request.user)
                chat.subscribers.add(user)
        messages = chat.messages.all().order_by('timestamp')
        datas = []
        for message in messages:
            datas.append(_make_message_serializable(message))
        return Response({
            'room': ChatRoomSerializer(
                _make_chatroom_serializable(request, chat)).data,
            'messages': MessageSerializer(datas, many=True).data
        })


class ChatRoomDetailsView(APIView):
    """
    View to return all messages in a Chat Room

    * Required logged in User

    get:
    Return list of message in the room

    post:
    Create a new message in specified room if the user is a subscriber

    """
    permission_classes = (
        IsAuthenticated, IsChatRoomSubscriber, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']
    parser_classes = (
        parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser)

    def get(self, request, chat_id, format=None):
        try:
            chatroom = ChatRoom.objects.get(id=chat_id)
        except ChatRoom.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, chatroom)
        messages = chatroom.messages.all().order_by('timestamp')
        datas = []
        for message in messages:
            data = _make_message_serializable(message)
            datas.append(data)
        serializer_data = MessageSerializer(datas, many=True).data
        return Response({
            'room_id': chatroom.id,
            'chats': serializer_data
        })

    def post(self, request, chat_id, format=None):
        try:
            chatroom = ChatRoom.objects.get(id=chat_id)
        except ChatRoom.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, chatroom)
        if request.data.get('content') or request.data.get('file'):
            message = Message(user=request.user)
            message.content = request.data.get('content')
            message.room = chatroom
            otherusers = []
            for user in chatroom.subscribers.all():
                if user != request.user:
                    otherusers.append(user)
            if otherusers:
                message.to_user = otherusers[0]
            else:
                for user in chatroom.unsubscribers.all():
                    if user != request.user:
                        message.to_user = user
            if request.data.get('file'):
                path, filetype = handle_attachment(
                    request.data.get('file'), chatroom.name)
                message.attachment_path = path
                message.attachment_type = filetype
            message.save()
            message_data = _make_message_serializable(message)
            message_serializer = MessageSerializer(data=message_data)
            if message_serializer.is_valid():
                if otherusers:
                    message_dict = {
                        'chatroom': ChatRoomSerializer(
                            _make_chatroom_serializable(
                                request, chatroom, for_ws=True)).data,
                        'message': message_serializer.data,
                        'type': 'add_message'
                    }
                    for otheruser in otherusers:
                        async_to_sync(channel_layer.group_send)(
                            '%s_messages' % otheruser.username,
                            {
                                'type': 'messenger.message',
                                'message': message_dict
                            }
                        )
                return Response({
                    'room': ChatRoomSerializer(_make_chatroom_serializable(
                        request, chatroom)).data,
                    'chat': message_serializer.data
                })
            return Response(
                message_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class DeleteMessageView(APIView):
    """
    This view will delete messages by ids
    """

    permission_classes = (
        IsAuthenticated, IsChatRoomSubscriber, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        messages = Message.objects.filter(id__in=request.data.get('ids'))
        otherusers = set()
        message_ids = []
        for message in messages:
            if message.user == request.user:
                chatroom = message.room
                for user in chatroom.subscribers.all():
                    if user != request.user:
                        otherusers.add(user)
                message_ids.append(message.id)
                message.delete()
        if otherusers:
            for otheruser in otherusers:
                async_to_sync(channel_layer.group_send)(
                    '%s_messages' % otheruser.username,
                    {
                        'type': 'messenger.message',
                        'message': {
                            'chatroom': chatroom.id,
                            'message_ids': message_ids,
                            'type': 'delete_message'
                        }
                    }
                )
        return Response({
            'room_id': chatroom.id,
            'message_ids': message_ids
        })


class DeleteChatRoomView(APIView):
    """
    This API will let an user delete a room
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        try:
            room = ChatRoom.objects.get(id=request.data.get('id'))
            if request.user in room.subscribers.all():
                room.subscribers.remove(request.user)
                room.unsubscribers.add(request.user)
                return Response({'id': room.id})
            return Response(status=status.HTTP_403_FORBIDDEN)
        except ChatRoom.DoesNotExist:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateReadStatusView(APIView):
    """
    This view will set messages read status
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        message_ids = request.data.get('message_ids')
        for message_id in message_ids:
            message = Message.objects.get(id=message_id)
            if message.user != request.user:
                message.read = True
                message.save()
        return Response()


def handle_attachment(attachment, chatroom_name):
    attachment_dir = os.path.join(
        settings.MEDIA_ROOT, 'messenger', chatroom_name)
    if not os.path.isdir(attachment_dir):
        os.makedirs(attachment_dir)
    dest_file_path = os.path.join(attachment_dir, attachment.name)
    if os.path.isfile(dest_file_path):
        attachment_s = attachment.name.split('.')
        attachment_s[0] = attachment_s[0] + '-' + get_random_string(length=6)
        if len(attachment_s) > 1:
            attachment_name = attachment_s[0] + '.' + attachment_s[1]
        else:
            attachment_name = attachment_s[0]
        dest_file_path = os.path.join(attachment_dir, attachment_name)
    with open(dest_file_path, 'wb') as attachment_file:
        for chunk in attachment.chunks():
            attachment_file.write(chunk)
    file_type = MimeTypes().guess_type(dest_file_path)[0]
    file_url = "%smessenger/%s/%s" % (
        settings.MEDIA_URL, chatroom_name, dest_file_path.split('/')[-1])
    return file_url, file_type or 'Unknown'
