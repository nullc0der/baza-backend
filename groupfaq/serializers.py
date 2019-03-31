from django.conf import settings

from rest_framework import serializers


class FaqJSONUploadSerializer(serializers.Serializer):
    api_key = serializers.CharField(required=True)
    faqfile = serializers.FileField(required=True)

    def validate_api_key(self, value):
        if value == settings.FAQ_API_KEY:
            return value
        raise serializers.ValidationError(
            'Api key is invalid'
        )
