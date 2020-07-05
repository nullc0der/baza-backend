from rest_framework import serializers

from webwallet.models import UserWebWallet
from webwallet.api_wrapper import ApiWrapper


class UserWebWalletSerializer(serializers.ModelSerializer):
    address = serializers.CharField(read_only=True)
    balance = serializers.SerializerMethodField()

    def get_balance(self, obj):
        apiwrapper = ApiWrapper()
        balance_res = apiwrapper.get_subwallet_balance(
            obj.address)
        if balance_res.status_code == 200:
            return balance_res.json()
        return {"unlocked": 0, "locked": 0}

    class Meta:
        model = UserWebWallet
        fields = ('id', 'name', 'address', 'balance', 'is_default')


class UserWebWalletTxSerializer(serializers.Serializer):
    source_address = serializers.CharField()
    destination_address = serializers.CharField()
    amount = serializers.IntegerField()

    def validate_source_address(self, value):
        wallets = self.context['request'].user.wallets.filter(address=value)
        if wallets:
            return value
        raise serializers.ValidationError('Invalid source address')

    def validate_destination_address(self, value):
        apiwrapper = ApiWrapper()
        res = apiwrapper.validate_address(value)
        if res.status_code == 200:
            return value
        raise serializers.ValidationError('Invalid destination address')

    def validate(self, data):
        apiwrapper = ApiWrapper()
        res = apiwrapper.get_subwallet_balance(data['source_address'])
        if res.status_code == 200:
            unlocked_balance = res.json()['unlocked']
            # TODO: Set default tx fee to config
            if data['amount'] + 1000 < unlocked_balance:
                return data
            raise serializers.ValidationError(
                'Requested amount is larger than balance')
        raise serializers.ValidationError(
            'Network issue occured, please try later')
