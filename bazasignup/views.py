from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser

from oauth2_provider.contrib.rest_framework import TokenHasScope

from bazasignup.models import (
    BazaSignup,
    BazaSignupAddress,
    BazaSignupAdditionalInfo,
    BazaSignupEmail,
    BazaSignupPhone,
    EmailVerification,
    PhoneVerification
)
from bazasignup.serializers import (
    UserInfoTabSerializer,
    EmailSerializer,
    EmailVerificationSerializer,
    PhoneSerializer,
    PhoneVerificationSerializer,
    SignupImageSerializer,
    BazaSignupListSerializer,
    BazaSignupSerializer
)
from bazasignup.tasks import (
    task_send_email_verification_code,
    task_send_email_verification_code_again,
    task_send_phone_verification_code,
    task_send_phone_verification_code_again
)


SKIPPABLE_INDEXES = [1, 2]


def get_current_completed_steps(request, current_step):
    try:
        signup = BazaSignup.objects.get(
            user=request.user)
        if current_step not in signup.get_completed_steps():
            completed_steps = signup.get_completed_steps()
            completed_steps.append(current_step)
            signup.completed_steps = ','.join(completed_steps)
            signup.save()
        return signup.completed_steps
    except BazaSignup.DoesNotExist:
        return "0"


def get_step_response(signup, current_step=0):
    next_step_index = get_next_step_index(signup.get_completed_steps())
    data = {
        'status': signup.status,
        'completed_steps': signup.get_completed_steps(),
        'next_step': {
            'index': next_step_index,
            'is_skippable': next_step_index in SKIPPABLE_INDEXES
        }
    }
    return Response(data)


def get_next_step_index(completed_steps):
    completed_steps = list(map(lambda x: int(x), completed_steps))
    not_completed_steps = []
    for i in range(4):
        if i not in completed_steps:
            not_completed_steps.append(i)
    return min(not_completed_steps) if len(not_completed_steps) else None


class CheckCompletedTab(views.APIView):
    """
    This API returns a list of signup completed tabs
    by user with signup status
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        try:
            signup = BazaSignup.objects.get(
                user=request.user)
            next_step_index = get_next_step_index(signup.get_completed_steps())
            data = {
                'status': signup.status,
                'completed_steps': signup.get_completed_steps(),
                'next_step': {
                    'index': next_step_index,
                    'is_skippable':
                    next_step_index in SKIPPABLE_INDEXES
                }
            }
        except BazaSignup.DoesNotExist:
            data = {
                'status': 'pending',
                'completed_steps': [],
                'next_step': {
                    'index': 0,
                    'is_skippable': 0 in SKIPPABLE_INDEXES
                }
            }
        return Response(data)


class UserInfoTabView(views.APIView):
    """
    This API collects user info tabs data and saves
    to respective models
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    # TODO: decide wheather an user will be able to edit info twice
    def post(self, request, format=None):
        serializer = UserInfoTabSerializer(data=request.data)
        if serializer.is_valid():
            signup, created = BazaSignup.objects.get_or_create(
                user=request.user,
                referral_code=serializer.validated_data['referral_code'],
                completed_steps=get_current_completed_steps(request, "0")
            )
            bazasignupaddress = BazaSignupAddress(
                signup=signup,
                address_type='user_input',
                house_number=serializer.validated_data['house_number'],
                street=serializer.validated_data['street_name'],
                zip_code=serializer.validated_data['zip_code'],
                city=serializer.validated_data['city'],
                state=serializer.validated_data['state'],
                country=serializer.validated_data['country']
            )
            bazasignupaddress.save()
            bazasignupadditionalinfo = BazaSignupAdditionalInfo(
                signup=signup,
                birth_date=serializer.validated_data['birthdate']
            )
            bazasignupadditionalinfo.save()
            request.user.first_name = serializer.validated_data['first_name']
            request.user.last_name = serializer.validated_data['last_name']
            request.user.save()
            return get_step_response(signup, current_step=0)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SkipEmailTabView(views.APIView):
    """
    This API will let user skip email verification step
    and let them continue to next step
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        try:
            signup = BazaSignup.objects.get(
                user=request.user
            )
            signup.completed_steps = get_current_completed_steps(request, "1")
            signup.email_skipped = True
            signup.save()
            return get_step_response(signup, current_step=1)
        except BazaSignup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class InitiateEmailVerificationView(views.APIView):
    """
    This API will fetch the users email and send verification
    code to user
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            signup = BazaSignup.objects.get(
                user=request.user
            )
            task_send_email_verification_code.delay(
                serializer.validated_data['email'], signup.id
            )
            return Response()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ValidateEmailVerificationCode(views.APIView):
    """
    This API will validate the verification code
    and send user to next step
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            emailverification = EmailVerification.objects.get(
                verification_code=serializer.validated_data['code']
            )
            signup = emailverification.signup
            signup.email = emailverification.email
            signup.completed_steps = get_current_completed_steps(request, "1")
            signup.save()
            bazasignupemail, created = BazaSignupEmail.objects.get_or_create(
                email=emailverification.email
            )
            bazasignupemail.signups.add(signup)
            emailverification.delete()
            return get_step_response(signup, current_step=1)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendVerificationEmailAgain(views.APIView):
    """
    This API will send verification code for a user again
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        try:
            signup = BazaSignup.objects.get(
                user=request.user
            )
            if hasattr(signup, 'emailverification'):
                task_send_email_verification_code_again.delay(signup.id)
                return Response()
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except BazaSignup.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class SkipPhoneTabView(views.APIView):
    """
    This API will let user skip phone verification step
    and let them continue to next step
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        try:
            signup = BazaSignup.objects.get(
                user=request.user
            )
            signup.completed_steps = get_current_completed_steps(request, "2")
            signup.phone_skipped = True
            signup.save()
            return get_step_response(signup, current_step=2)
        except BazaSignup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class InitiatePhoneVerificationView(views.APIView):
    """
    This API will fetch the users phone number and send verification
    code to user
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        serializer = PhoneSerializer(data=request.data)
        if serializer.is_valid():
            signup = BazaSignup.objects.get(
                user=request.user
            )
            task_send_phone_verification_code.delay(
                signup.id, serializer.validated_data['phone']
            )
            return Response()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ValidatePhoneVerificationCode(views.APIView):
    """
    This API will validate the verification code
    and send user to next step
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        serializer = PhoneVerificationSerializer(data=request.data)
        if serializer.is_valid():
            phoneverification = PhoneVerification.objects.get(
                verification_code=serializer.validated_data['code']
            )
            signup = phoneverification.signup
            signup.phone_number = phoneverification.phone_number
            signup.completed_steps = get_current_completed_steps(request, "2")
            signup.save()
            bazasignupphone, created = BazaSignupPhone.objects.get_or_create(
                phone_number=phoneverification.phone_number
            )
            bazasignupphone.signups.add(signup)
            phoneverification.delete()
            return get_step_response(signup, current_step=2)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendVerificationSMSAgain(views.APIView):
    """
    This API will send verification code sms for an user again
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        try:
            signup = BazaSignup.objects.get(
                user=request.user
            )
            if hasattr(signup, 'phoneverification'):
                task_send_phone_verification_code_again.delay(signup.id)
                return Response()
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except BazaSignup.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class SignupImageUploadView(views.APIView):
    """
    This API will be used to upload an image document or photo
    of the user
    """

    parser_classes = (FormParser, MultiPartParser, )
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        serializer = SignupImageSerializer(data=request.data)
        if serializer.is_valid():
            signup = BazaSignup.objects.get(user=request.user)
            signup.photo = serializer.validated_data['image']
            signup.completed_steps = get_current_completed_steps(request, "3")
            signup.save()
            return get_step_response(signup, current_step=3)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def reset_signup(request):
    """
    TODO: Remove this before production
    """
    username = request.GET.get('username')
    try:
        user = User.objects.get(username=username)
        if hasattr(user, 'bazasignup'):
            user.bazasignup.delete()
        return HttpResponse('Done, Happy Testing :)')
    except User.DoesNotExist:
        return HttpResponse('The user can\'t be found '
                            'please check username')


class BazaSignupListView(views.APIView):
    """
    This API will be used to get all the signups list
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        datas = []
        signups = BazaSignup.objects.all()
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

    permission_classes = (IsAuthenticated, TokenHasScope, )
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
        data = {
            'id_': signup.id,
            'username': signup.user.username,
            'full_name': signup.user.get_full_name(),
            'email': signup.email,
            'phone_number': signup.phone_number,
            'photo': signup.photo.url if signup.photo else '',
            'birthdate': signup.bazasignupadditionalinfo.birth_date,
            'user_addresses': [
                self.get_address_data(address)
                for address in signup.addresses.all()],
            'status': signup.status,
            'signup_date': signup.signup_date,
            'verified_date': signup.verified_date,
            'referral_code': signup.referral_code,
            'wallet_address': signup.wallet_address,
            'on_distribution': signup.on_distribution
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
