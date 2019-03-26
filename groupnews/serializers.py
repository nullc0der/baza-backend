from rest_framework import serializers

from grouppost.serializers import GroupSerializer, UserSerializer
from groupnews.models import GroupNews, NewsImage


class NewsSerializer(serializers.ModelSerializer):
    editor = UserSerializer(required=False)
    basic_group = GroupSerializer(required=False)
    impressioncount = serializers.ReadOnlyField()
    converted_news = serializers.ReadOnlyField()

    class Meta:
        model = GroupNews
        fields = '__all__'


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ('image', )
