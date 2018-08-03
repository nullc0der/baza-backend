from rest_framework import serializers

from userprofile.serializers import UserSerializer
from stripepayment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Payment
        fields = (
            'id',
            'user',
            'name',
            'amount',
            'is_success',
            'message',
            'payment_type',
            'fail_reason',
            'charge_id',
            'date'
        )
