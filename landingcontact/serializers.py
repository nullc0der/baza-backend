from rest_framework import serializers

from landingcontact.models import LandingContact


class LandingContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingContact
        fields = (
            'id', 'name', 'email',
            'subject', 'message'
        )
