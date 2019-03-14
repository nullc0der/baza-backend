from rest_framework.views import APIView
from rest_framework.response import Response

from donation.models import Donation
from bazasignup.models import BazaSignup


class LandingStats(APIView):
    """
    This API will be used to get all stats required in
    landing page except following
        * Recent donors list
        * Total purchased coins
    """

    def get_donation_stats(self):
        collected = 0
        donations = Donation.objects.filter(is_pending=False)
        for donation in donations:
            collected += donation.amount
        return {
            'collected': collected if collected != 0 else 10,
            'required': 1500,
            'total_donors': donations.count()
        }

    def get_distribution_stats(self):
        signups = BazaSignup.objects.filter(status='approved')
        return {'total_approved_signups': signups.count()}

    def get(self, request, format=None):
        return Response({
            "donation": self.get_donation_stats(),
            "distribution": self.get_distribution_stats()
        })
