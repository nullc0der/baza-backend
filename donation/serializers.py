from rest_framework import serializers


class AnonDonationSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    name = serializers.CharField(error_messages={
        'blank': 'This field is required'
    })
    email = serializers.EmailField(error_messages={
        'blank': 'This field is required'
    })
    phone_no = serializers.RegexField(
        r'^(\+)(\d{11,15})$',
        allow_blank=True,
        error_messages={
            'invalid':
                'Please enter a valid phone number'
        }
    )

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError('Enter a non zero amount')
        if value < 0:
            raise serializers.ValidationError('Negative amount not allowed')
        return value


class DonationSerializer(serializers.Serializer):
    amount = serializers.FloatField()

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError('Enter a non zero amount')
        if value < 0:
            raise serializers.ValidationError('Negative amount not allowed')
        return value
