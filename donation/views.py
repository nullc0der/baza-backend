from random import randint

from django.conf import settings
from django.db.models import Q

from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

# from coinbasepay.models import Charge
# from coinbasepay.utils import create_charge
# from coinbasepay.dicts import CHARGE

from ekatagp.utils import create_payment_form
from ekatagp.models import PaymentForm

from userprofile.utils import get_profile_photo
from authclient.utils import AuthHelperClient

from donation.models import Donation
from donation.serializers import DonationSerializer, AnonDonationSerializer


URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


def get_users_name(user):
    name = user.get_full_name()
    if not name:
        name = user.profile.username or user.username
    return name


def get_users_phone_no(user):
    phone_no = user.profile.phones.filter(
        Q(primary=True) & Q(verified=True)
    )
    if len(phone_no):
        return phone_no[0].phone_number
    return ''


def get_users_primary_email(access_token):
    authhelperclient = AuthHelperClient(
        URL_PROTOCOL +
        settings.CENTRAL_AUTH_INTROSPECT_URL +
        '/authhelper/useremails/'
    )
    return authhelperclient.get_user_primary_email(access_token)


def get_initiate_donation_response(request, is_anonymous):
    serializer = AnonDonationSerializer(data=request.data) \
        if is_anonymous else DonationSerializer(data=request.data)
    if serializer.is_valid():
        form_id = create_payment_form(serializer.validated_data['amount'])
        if form_id:
            payment_form = PaymentForm.objects.get(form_id=form_id)
            Donation.objects.create(
                user=None if is_anonymous else request.user,
                amount=serializer.validated_data['amount'],
                name=serializer.validated_data.get('name', '')
                if is_anonymous else get_users_name(request.user),
                phone_no=serializer.validated_data.get('phone_no', '')
                if is_anonymous else get_users_phone_no(request.user),
                email=serializer.validated_data.get('email')
                if is_anonymous else get_users_primary_email(
                    request.META['HTTP_AUTHORIZATION'].split(' ')[1]),
                logged_ip=request.META.get(
                    'HTTP_CF_CONNECTING_IP', ''),
                ekatagp_form=payment_form,
                is_anonymous=serializer.validated_data['is_anonymous']
            )
            return Response({
                'form_id': form_id
            })
        return Response({
            'non_field_errors': [
                'There is an issue initiating your payment,'
                'please try later']
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(
        serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_donation_closed_response():
    return Response({
        'non_field_errors': ['Thank you for your support but'
                             ' donation is disabled for sometime']
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InitiateDonationView(views.APIView):
    """
    This view will be used for creating a donation and initiating
    a ekatagp form
     * Required logged in user
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        return get_initiate_donation_response(request, False)
        # return get_donation_closed_response()


class InitiateAnonymousDonationView(views.APIView):
    """
    This view will be used for creating a donation and initiating
    a ekatagp form
    """

    def post(self, request, format=None):
        return get_initiate_donation_response(request, True)
        # return get_donation_closed_response()


class GetLatestDonations(views.APIView):
    """
    This view will be used to get latest 10 donations
    """

    def get_donator_image_url(self, donation):
        image_url = None
        if not donation.is_anonymous and donation.user:
            image_url = get_profile_photo(donation.user)
        return image_url if image_url else \
            'https://api.adorable.io/avatars/80' +\
            '/abott{0}@adorable.io.png'.format(
                randint(0, 9))

    def get_donations(self):
        datas = []
        donations = Donation.objects.filter(
            is_pending=False).order_by('-id')
        donations = donations if len(donations) <= 10 else donations[0:10]
        for donation in donations:
            data = {
                'name': donation.name
                if not donation.is_anonymous else 'Anonymous Donor',
                'amount': donation.amount,
                'donated_on': donation.donated_on,
                'donator_image_url':
                    self.get_donator_image_url(donation)
            }
            datas.append(data)
        return datas

    def get(self, request, format=None):
        return Response(self.get_donations())
