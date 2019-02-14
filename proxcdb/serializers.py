from rest_framework import serializers
from userprofile.serializers import UserSerializer
from proxcdb.models import ProxcAccount, ProxcTransaction


class ProxcAccountSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ProxcAccount
        fields = ('user', )


class ProxcTransactionSerializer(serializers.ModelSerializer):
    account = ProxcAccountSerializer(required=False)
    to_account = ProxcAccountSerializer(required=False)
    receipt_link = serializers.SerializerMethodField()

    def get_receipt_link(self, obj):
        if obj.coinpurchase:
            return obj.coinpurchase.coinbase_charge.get_receipt_url()
        return None

    def validate_amount(self, value):
        proxcaccount = self.context['proxcaccount']
        if value == 0:
            raise serializers.ValidationError('Enter a non zero amount')
        if value < 0:
            raise serializers.ValidationError('Negative amount not allowed')
        if proxcaccount.balance < (value + 0.01):
            raise serializers.ValidationError('Insufficient funds')
        return value

    class Meta:
        model = ProxcTransaction
        fields = (
            'id',
            'account',
            'to_account',
            'message',
            'txid',
            'status',
            'timestamp',
            'amount',
            'receipt_link'
        )
