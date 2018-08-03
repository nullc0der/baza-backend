from rest_framework import serializers


class CoinPurchaseSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    stripe_token = serializers.CharField()

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError('Enter a non zero amount')
        if value < 0:
            raise serializers.ValidationError('Negative amount not allowed')
        return value
