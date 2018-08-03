from django.conf import settings

from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from stripepayment.utils import StripePayment

from donation.models import Donation
from donation.serializers import DonationSerializer


def get_donation_response(request, is_anonymous):
    serializer = DonationSerializer(data=request.data)
    if serializer.is_valid():
        stripe_payment = StripePayment(
            user=None if is_anonymous else request.user,
            fullname=serializer.validated_data['name']
        )
        payment = stripe_payment.process_payment(
            token=serializer.validated_data['stripe_token'],
            payment_type='donation',
            amount=serializer.validated_data['amount'],
            message=''
        )
        if payment.is_success:
            Donation.objects.create(
                user=None if is_anonymous else request.user,
                amount=serializer.validated_data['amount'],
                name=serializer.validated_data['name'],
                phone_no=serializer.validated_data['phone_no'],
                email=serializer.validated_data['email'],
                stripe_payment=payment
            )
            return Response()
        return Response({
            'non_field_errors': [
                'There is an issue processing your payment,'
                'please try later']
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(
        serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DonationView(views.APIView):
    """
    This view will be used for creating a donation and charging
    the card using stripe
     * Required logged in user
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        return get_donation_response(request, False)


class AnonymousDonationView(views.APIView):
    """
    This view will be used for creating a donation and charging
    the card using stripe
    """

    def post(self, request, format=None):
        return get_donation_response(request, True)
