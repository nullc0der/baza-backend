import bleach
from django.conf import settings
from rest_framework import serializers

from grouppost.serializers import GroupSerializer, UserSerializer
from groupnews.models import GroupNews, NewsImage


class NewsSerializer(serializers.ModelSerializer):
    editor = UserSerializer(required=False)
    basic_group = GroupSerializer(required=False)
    impressioncount = serializers.ReadOnlyField()

    def validate_news(self, value):
        cleaned_text = bleach.clean(
            value,
            settings.BLEACH_VALID_TAGS,
            settings.BLEACH_VALID_ATTRS,
            settings.BLEACH_VALID_STYLES
        )
        return cleaned_text  # sanitize markdown

    class Meta:
        model = GroupNews
        fields = '__all__'


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ('image', )
