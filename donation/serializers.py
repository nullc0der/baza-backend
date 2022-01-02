from rest_framework import serializers


class AnonDonationSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    name = serializers.CharField(allow_blank=True)
    email = serializers.EmailField(allow_blank=True)
    phone_no = serializers.RegexField(
        r'^(\+)(\d{11,15})$',
        allow_blank=True,
        error_messages={
            'invalid':
                'Please enter a valid phone number'
        }
    )
    is_anonymous = serializers.BooleanField()

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError('Enter a non zero amount')
        if value < 0:
            raise serializers.ValidationError('Negative amount not allowed')
        return value

    def validate(self, values):
        if not values['is_anonymous'] and not values['name']\
                and not values['email']:
            raise serializers.ValidationError(
                {
                    'name': 'Name is required if not an anonymous donation',
                    'email': 'Email id is required if'
                    ' not an anonymous donation'
                })
        return values


class DonationSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    is_anonymous = serializers.BooleanField()

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError('Enter a non zero amount')
        if value < 0:
            raise serializers.ValidationError('Negative amount not allowed')
        return value
