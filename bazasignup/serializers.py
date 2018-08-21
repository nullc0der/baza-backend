from rest_framework import serializers

from bazasignup.countries import COUNTRIES


class UserInfoTabSerializer(serializers.Serializer):
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
