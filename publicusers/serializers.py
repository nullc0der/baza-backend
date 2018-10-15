from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    username = serializers.CharField(max_length=200, required=True)
    fullname = serializers.CharField(max_length=200, allow_blank=True)
    user_image_url = serializers.CharField(max_length=200, allow_blank=True)
    user_avatar_color = serializers.CharField(max_length=200, allow_blank=True)
