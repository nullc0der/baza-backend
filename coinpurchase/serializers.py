from rest_framework import serializers


class CoinPurchaseSerializer(serializers.Serializer):
    price = serializers.FloatField()
    currency = serializers.CharField()
    coin_name = serializers.CharField()
    stripe_token = serializers.CharField()

    def validate_price(self, value):
        if value == 0:
            raise serializers.ValidationError('Enter a non zero amount')
        if value < 0:
            raise serializers.ValidationError('Negative amount not allowed')
        return value
