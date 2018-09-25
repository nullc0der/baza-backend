from django.contrib.auth.models import User
from rest_framework import serializers

from userprofile.models import (
    UserProfile,
    UserPhoto,
    UserProfilePhoto,
    UserDocument
)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    def validate_username(self, value):
        try:
            user = User.objects.get(username=value)
            if user == self.context['request'].user:
                return value
            raise serializers.ValidationError(
                'A user with that name already exist'
            )
        except User.DoesNotExist:
            return value

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'date_joined')


class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhoto
        fields = ('id', 'photo')


class UserProfilePhotoSerializer(serializers.ModelSerializer):
    userphoto = UserPhotoSerializer(read_only=True)

    class Meta:
        model = UserProfilePhoto
        fields = ('id', 'userphoto', 'is_active')


class UserDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocument
        fields = ('id', 'document')


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    def update(self, instance, validated_data):
        user = validated_data.get('user', {})
        instance.user.first_name = user.get(
            'first_name', instance.user.first_name)
        instance.user.last_name = user.get(
            'last_name', instance.user.last_name)
        instance.user.username = user.get(
            'username', instance.user.username)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.about_me = validated_data.get('about_me', instance.about_me)
        instance.website = validated_data.get('website', instance.website)
        instance.location = validated_data.get('location', instance.location)
        instance.user.save()
        instance.save()
        return instance

    class Meta:
        model = UserProfile
        fields = (
            'id', 'user', 'gender', 'about_me', 'website',
            'location', 'phone_number', 'default_avatar_color')
