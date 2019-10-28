from rest_framework import serializers

from landingcontact.models import LandingContact


class LandingContactSerializer(serializers.ModelSerializer):
    token = serializers.CharField()

    def create(self, validated_data):
        validated_data.pop('token', None)
        return super().create(validated_data)

    class Meta:
        model = LandingContact
        fields = (
            'id', 'name', 'email',
            'subject', 'message',
            'token'
        )
