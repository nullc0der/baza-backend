from django.conf import settings

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from bazasignup.models import (
    BazaSignup,
    BazaSignupEmail,
    BazaSignupPhone
)
from bazasignup.serializers import (
    BazaSignupListSerializer,
    BazaSignupSerializer
)
from bazasignup.permissions import IsStaffOfSiteOwnerGroup


class BazaSignupListView(views.APIView):
    """
    This API will be used to get all the signups list
    """

    permission_classes = (IsAuthenticated, TokenHasScope,
                          IsStaffOfSiteOwnerGroup, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        datas = []
        signups = BazaSignup.objects.all().order_by('-id')
        for signup in signups:
            data = {
                'id_': signup.id,
                'username': signup.user.username,
                'status': signup.status
            }
            datas.append(data)
        serializer = BazaSignupListSerializer(datas, many=True)
        return Response(serializer.data)


class BazaSignupDetailsView(views.APIView):
    """
    This API will be used to get data for a specific signup id
    """

    permission_classes = (IsAuthenticated, TokenHasScope,
                          IsStaffOfSiteOwnerGroup)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get_address_data(self, address):
        data = {
            'address_type': address.address_type,
            'country': address.country,
            'city': address.city,
            'state': address.state,
            'house_number': address.house_number,
            'street_name': address.street,
            'zip_code': address.zip_code,
            'latitude': address.latitude,
            'longitude': address.longitude
        }
        return data

    def get_signup_data(self, signup):
        email_used_before = False
        phone_used_before = False
        if signup.email:
            bazasignupemail = BazaSignupEmail.objects.get(
                email=signup.email
            )
            email_used_before = bazasignupemail.signups.count() > 1
        if signup.phone_number:
            bazasignupphone = BazaSignupPhone.objects.get(
                phone_number=signup.phone_number
            )
            phone_used_before = bazasignupphone.signups.count() > 1
        data = {
            'id_': signup.id,
            'username': signup.user.username,
            'full_name': signup.user.get_full_name(),
            'email': signup.email,
            'email_used_before': email_used_before,
            'phone_number': signup.phone_number,
            'phone_used_before': phone_used_before,
            'photo': signup.photo.url if signup.photo else '',
            'birthdate': signup.bazasignupadditionalinfo.birth_date,
            'user_addresses': [
                self.get_address_data(address)
                for address in signup.addresses.all()],
            'status': signup.status,
            'signup_date': signup.signup_date,
            'verified_date': signup.verified_date,
            'referral_code': signup.bazasignupreferralcode.code
            if hasattr(signup, 'bazasignupreferralcode') else '',
            'wallet_address': signup.wallet_address,
            'on_distribution': signup.on_distribution,
            'auto_approval_fail_reasons':
            signup.bazasignupautoapprovalfailreason_set.all()
        }
        return data

    def get(self, request, signup_id, format=None):
        try:
            bazasignup = BazaSignup.objects.get(id=signup_id)
            datas = self.get_signup_data(bazasignup)
            serializer = BazaSignupSerializer(datas)
            return Response(serializer.data)
        except BazaSignup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, signup_id, format=None):
        try:
            bazasignup = BazaSignup.objects.get(id=signup_id)
            serializer = BazaSignupSerializer(data=request.data, partial=True)
            if serializer.is_valid():
                if 'on_distribution' in serializer.validated_data:
                    bazasignup.on_distribution = serializer.validated_data[
                        'on_distribution']
                if 'status' in serializer.validated_data:
                    bazasignup.status = serializer.validated_data['status']
                bazasignup.changed_by = request.user
                bazasignup.save()
                serializer.validated_data['id_'] = bazasignup.id
                return Response(serializer.validated_data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except BazaSignup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
