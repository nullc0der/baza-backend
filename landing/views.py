from django.conf import settings
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response

from donation.models import Donation
from bazasignup.models import BazaSignup
from proxcdb.models import ProxcTransaction
from webwallet.api_wrapper import ApiWrapper, from_atomic


class LandingStats(APIView):
    """
    This API will be used to get all stats required in
    landing page except following
        * Recent donors list
        * Total purchased coins
    """

    def calculate_total_baza_distributed(self):
        transactions = ProxcTransaction.objects.filter(
            message='per_minute_baza_distribution')
        amounts = [transaction.amount for transaction in transactions]
        return sum(amounts)

    def get_main_wallet_balance(self):
        apiwrapper = ApiWrapper()
        res = apiwrapper.get_subwallet_balance(
            settings.PROXC_TO_REAL_FROM_ADDRESS)
        if res.status_code == 200:
            return from_atomic(res.json()['unlocked'])

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
        distribution_stats = cache.get('distribution_stats')
        if distribution_stats:
            return distribution_stats
        distribution_stats = {
            'total_approved_signups': BazaSignup.objects.filter(
                status='approved').count(),
            'distribution_main_wallet_balance': self.get_main_wallet_balance(),
            'total_amount_distributed': self.calculate_total_baza_distributed()
        }
        cache.set('distribution_stats', distribution_stats,
                  60*60)  # Cached for 1 hour
        return distribution_stats

    def get(self, request, format=None):
        return Response({
            "donation": self.get_donation_stats(),
            "distribution": self.get_distribution_stats()
        })
