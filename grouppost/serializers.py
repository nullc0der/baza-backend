import bleach
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers

from userprofile.models import UserProfilePhoto
from group.models import BasicGroup
from grouppost.models import GroupPost, PostComment, PostImage


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicGroup
        fields = ('id', 'name')


class UserSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    user_image_url = serializers.SerializerMethodField()
    user_avatar_color = serializers.SerializerMethodField()

    def get_username(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.username or obj.username
        return obj.username

    def get_fullname(self, obj):
        return obj.get_full_name()

    def get_user_image_url(self, obj):
        profile_photo = None
        try:
            profilephoto = obj.profile.profilephotos.get(
                is_active=True)
            profile_photo = profilephoto.userphoto.photo.url
        except UserProfilePhoto.DoesNotExist:
            pass
        return profile_photo

    def get_user_avatar_color(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.default_avatar_color
        return '#000000'

    class Meta:
        model = User
        fields = ('id', 'username', 'fullname',
                  'user_image_url', 'user_avatar_color')


class PostSerializer(serializers.ModelSerializer):
    creator = UserSerializer(required=False)
    basic_group = GroupSerializer(required=False)
    approved_by = UserSerializer(required=False)
    converted_post = serializers.ReadOnlyField()
    created_date = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField(required=False)

    def get_created_date(self, obj):
        return obj.created_on.date()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def validate_post(self, value):
        cleaned_text = bleach.clean(
            value,
            settings.BLEACH_VALID_TAGS,
            settings.BLEACH_VALID_ATTRS,
            settings.BLEACH_VALID_STYLES
        )
        return cleaned_text  # sanitize markdown

    class Meta:
        model = GroupPost
        fields = '__all__'


class CommentSerialzer(serializers.ModelSerializer):
    commentor = UserSerializer(required=False)
    post = PostSerializer(required=False)
    approved_by = UserSerializer(required=False)

    class Meta:
        model = PostComment
        fields = '__all__'


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('image', )
