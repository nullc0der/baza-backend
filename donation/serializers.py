from rest_framework import serializers


class DonationSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    name = serializers.CharField()
    email = serializers.EmailField(write_only=True)
    phone_no = serializers.RegexField(
        r'^(\+)(\d{11,15})$',
        allow_blank=True,
        error_messages={
            'invalid':
                'Please enter a valid phone number'
        },
        write_only=True
    )
    donated_on = serializers.DateTimeField(read_only=True)
    donator_image_url = serializers.URLField(read_only=True)

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError('Enter a non zero amount')
        if value < 0:
            raise serializers.ValidationError('Negative amount not allowed')
        return value
