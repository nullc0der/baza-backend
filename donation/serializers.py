from rest_framework import serializers


class DonationSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    name = serializers.CharField()
    email = serializers.EmailField()
    phone_no = serializers.RegexField(r'^(\+)(\d{12})$')
    stripe_token = serializers.CharField()

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError('Enter a non zero amount')
        if value < 0:
            raise serializers.ValidationError('Negative amount not allowed')
        return value
