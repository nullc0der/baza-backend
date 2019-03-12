from datetime import timedelta

from django.contrib.auth.models import User
from django.conf import settings
from django.utils.timezone import now
from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField

from phoneverification.models import PhoneVerification
from userprofile.models import (
    UserProfile,
    UserPhoto,
    UserProfilePhoto,
    UserDocument,
    UserPhone
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name', 'date_joined', 'last_login')


class UserPhotoSerializer(serializers.ModelSerializer):
    photo = Base64ImageField()

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


class UserPhoneSerializer(serializers.ModelSerializer):
    verified = serializers.ReadOnlyField()

    def validate_phone_number(self, value):
        if self.instance and value != self.instance.phone_number:
            raise serializers.ValidationError(
                'Phone number can\'t be edited once set'
            )
        userphones = UserPhone.objects.filter(
            phone_number=value)
        if userphones.count() >= 1:
            raise serializers.ValidationError(
                'Double entry is not allowed'
            )
        return value

    class Meta:
        model = UserPhone
        fields = ('id', 'phone_number', 'phone_number_country_code',
                  'phone_number_type', 'primary', 'verified')


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    def validate_username(self, value):
        if value:
            try:
                userprofile = UserProfile.objects.get(username=value)
                if userprofile == self.context['request'].user.profile:
                    return value
                raise serializers.ValidationError(
                    'A user with that name already exist'
                )
            except UserProfile.DoesNotExist:
                return value
        return value

    def update(self, instance, validated_data):
        user = validated_data.get('user', {})
        instance.user.first_name = user.get(
            'first_name', instance.user.first_name)
        instance.user.last_name = user.get(
            'last_name', instance.user.last_name)
        instance.username = validated_data.get('username', instance.username)
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
            'id', 'user', 'username', 'gender', 'about_me', 'website',
            'location', 'phone_number', 'default_avatar_color')


class UserPhoneValidationSerializer(serializers.Serializer):
    verification_code = serializers.CharField()

    def validate_verification_code(self, value):
        try:
            phoneverification = PhoneVerification.objects.get(
                verification_code=value
            )
            if phoneverification.created_on + timedelta(
                seconds=settings.PHONE_VERIFICATION_CODE_EXPIRES_IN)\
                    > now():
                return value
            raise serializers.ValidationError(
                "This code is expired"
            )
        except PhoneVerification.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid code"
            )
