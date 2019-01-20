from rest_framework import serializers

from userprofile.models import UserTwoFactorRecovery


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class TwoFactorSerializer(serializers.Serializer):
    code = serializers.CharField()
    uuid = serializers.UUIDField()

    def validate_code(self, value):
        user = self.context['user']
        if user.two_factor.verify_totp(value):
            return value
        try:
            recovery_code = user.two_factor_recovery.get(code=value)
            if recovery_code.valid:
                recovery_code.valid = False
                recovery_code.save()
                return value
        except UserTwoFactorRecovery.DoesNotExist:
            pass
        raise serializers.ValidationError('Code is invalid')


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
