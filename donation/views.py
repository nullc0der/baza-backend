from random import randint

from django.conf import settings

from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from coinbasepay.models import Charge
from coinbasepay.utils import create_charge
from coinbasepay.dicts import CHARGE

from userprofile.views import get_profile_photo

from donation.models import Donation
from donation.serializers import DonationSerializer


def get_initiate_donation_response(request, is_anonymous):
    serializer = DonationSerializer(data=request.data)
    if serializer.is_valid():
        charge_id = create_charge(
            amount=request.data.get('amount'),
            charge_name=CHARGE['2']['name'],
            charge_description=CHARGE['2']['description'],
            charged_for=CHARGE['2']['charged_for'],
            charged_user=None if is_anonymous else request.user)
        if charge_id:
            charge = Charge.objects.get(charge_code=charge_id)
            Donation.objects.create(
                user=None if is_anonymous else request.user,
                amount=serializer.validated_data['amount'],
                name=serializer.validated_data['name'],
                phone_no=serializer.validated_data['phone_no'],
                email=serializer.validated_data['email'],
                logged_ip=request.META.get(
                    'HTTP_CF_CONNECTING_IP', ''),
                coinbase_charge=charge
            )
            return Response({
                'charge_id': charge_id
            })
        return Response({
            'non_field_errors': [
                'There is an issue initiating your payment,'
                'please try later']
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(
        serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InitiateDonationView(views.APIView):
    """
    This view will be used for creating a donation and initiating
    a coinbase charge
     * Required logged in user
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        return get_initiate_donation_response(request, False)


class InitiateAnonymousDonationView(views.APIView):
    """
    This view will be used for creating a donation and initiating
    a coinbase charge
    """

    def post(self, request, format=None):
        return get_initiate_donation_response(request, True)


class GetLatestDonations(views.APIView):
    """
    This view will be used to get latest 10 donations
    """

    def get_donator_image_url(self, user):
        image_url = None
        if user:
            image_url = get_profile_photo(user)
        return image_url if image_url else \
            'https://api.adorable.io/avatars/80' +\
            '/abott{0}@adorable.io.png'.format(
                randint(0, 9))

    def get_serializable_donations(self, donations):
        datas = []
        for donation in donations:
            data = {
                'name': donation.name,
                'amount': donation.amount,
                'donated_on': donation.donated_on,
                'donator_image_url':
                    self.get_donator_image_url(donation.user)
            }
            datas.append(data)
        return datas

    def get(self, request, format=None):
        donations = Donation.objects.filter(
            is_pending=False).order_by('-id')
        donations = donations if len(donations) < 10 else donations[10]
        serializer = DonationSerializer(
            self.get_serializable_donations(donations), many=True)
        return Response(serializer.data)


class GetDonationStats(views.APIView):
    """
    This API will be used to get total donation required and
    collected
    """

    def get(self, request, format=None):
        collected = 0
        donations = Donation.objects.filter(is_pending=False)
        for donation in donations:
            collected += donation.amount
        return Response({
            'collected': collected if collected != 0 else 10,
            'required': 1500
        })
