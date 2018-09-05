from datetime import timedelta
from django.utils.timezone import now

from rest_framework import serializers

from bazasignup.countries import COUNTRIES
from bazasignup.models import (
    EmailVerification,
    PhoneVerification
)


class AddressSerializer(serializers.Serializer):
    address_type = serializers.CharField(allow_blank=True)
    country = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    house_number = serializers.IntegerField()
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
    house_number = serializers.IntegerField()
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
            raise serializers.ValidationError(
                "This feature is not enabled yet, please"
                " leave this blank"
            )
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
    phone = serializers.CharField()


class PhoneVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=6, max_length=6)

    def validate_code(self, value):
        try:
            phoneverification = PhoneVerification.objects.get(
                verification_code=value
            )
            if phoneverification.created_on + timedelta(seconds=120) > now():
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


class BazaSignupSerializer(serializers.Serializer):
    id_ = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    photo = serializers.CharField()
    birthdate = serializers.DateField()
    user_addresses = AddressSerializer(many=True)
    status = serializers.CharField()
    signup_date = serializers.DateTimeField()
    verified_date = serializers.DateTimeField()
    referral_code = serializers.CharField()
    wallet_address = serializers.CharField()
    on_distribution = serializers.BooleanField()


class BazaSignupListSerializer(serializers.Serializer):
    id_ = serializers.IntegerField()
    username = serializers.CharField()
    status = serializers.CharField()
