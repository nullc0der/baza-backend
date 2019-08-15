from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now

from rest_framework import serializers

from phoneverification.models import PhoneVerification

from grouppost.serializers import UserSerializer

from bazasignup.countries import COUNTRIES
from bazasignup.models import (
    EmailVerification,
    BazaSignup,
    BazaSignupReferralCode,
    BazaSignupComment
)


class AddressSerializer(serializers.Serializer):
    address_type = serializers.CharField(allow_blank=True)
    country = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    house_number = serializers.CharField()
    street_name = serializers.CharField()
    zip_code = serializers.CharField()
    latitude = serializers.CharField()
    longitude = serializers.CharField()


class UserInfoTabSerializer(serializers.Serializer):
    # TODO: Use AddressSerializer here for address section
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    referral_code = serializers.CharField(allow_blank=True)
    country = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    house_number = serializers.CharField()
    street_name = serializers.CharField()
    zip_code = serializers.CharField()
    birthdate = serializers.DateField()

    def validate_country(self, value):
        if value not in COUNTRIES:
            raise serializers.ValidationError(
                "Enter a valid country name"
            )
        return value

    def validate_referral_code(self, value):
        if value:
            try:
                BazaSignupReferralCode.objects.get(code=value)
                return value
            except BazaSignupReferralCode.DoesNotExist:
                raise serializers.ValidationError('Invalid referral code')
        return value


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class EmailVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=6, max_length=6)

    def validate_code(self, value):
        try:
            emailverification = EmailVerification.objects.get(
                verification_code=value
            )
            if emailverification.created_on + timedelta(seconds=120) > now():
                return value
            raise serializers.ValidationError(
                "This code is expired, please click on send email again"
            )
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid code"
            )


class PhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False)
    phone_number_dial_code = serializers.CharField(required=False)


class PhoneVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=6, max_length=6)

    def validate_code(self, value):
        try:
            phoneverification = PhoneVerification.objects.get(
                verification_code=value
            )
            if phoneverification.created_on + timedelta(
                seconds=settings.PHONE_VERIFICATION_CODE_EXPIRES_IN)\
                    > now():
                return value
            raise serializers.ValidationError(
                "This code is expired, please click on send SMS again"
            )
        except PhoneVerification.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid code"
            )


class SignupImageSerializer(serializers.Serializer):
    image = serializers.ImageField()


class BazaSignupListSerializer(serializers.Serializer):
    id_ = serializers.IntegerField()
    status = serializers.CharField()
    fullname = serializers.CharField()
    username = serializers.CharField()
    user_image_url = serializers.CharField()
    user_avatar_color = serializers.CharField()


class BazaSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = BazaSignup
        fields = ('id', )


class BazaSignupCommentSerializer(serializers.ModelSerializer):
    commented_by = UserSerializer(required=False)
    signup = BazaSignupSerializer(required=False)

    class Meta:
        model = BazaSignupComment
        fields = '__all__'
