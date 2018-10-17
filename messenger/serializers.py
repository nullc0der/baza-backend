from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    username = serializers.CharField(max_length=200, required=True)
    user_image_url = serializers.CharField(max_length=200, allow_blank=True)
    user_avatar_color = serializers.CharField(max_length=200, allow_blank=True)


class ChatRoomSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    unread_count = serializers.IntegerField(default=0)
    user = UserSerializer()


class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    to_user = UserSerializer()
    user = UserSerializer()
    message = serializers.CharField(allow_blank=True)
    timestamp = serializers.DateTimeField()
    read = serializers.BooleanField()
    fileurl = serializers.CharField(max_length=500, allow_blank=True)
    filetype = serializers.CharField(max_length=40, allow_blank=True)
    filename = serializers.CharField(max_length=200, allow_blank=True)
