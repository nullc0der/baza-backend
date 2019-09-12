from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

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
    BazaSignupReferralCode
)
from bazasignup.serializers import (
    UserInfoTabSerializer,
    EmailSerializer,
    EmailVerificationSerializer,
    PhoneSerializer,
    PhoneVerificationSerializer,
    SignupImageSerializer
)
from phoneverification.tasks import task_send_phone_verification_code
from phoneverification.models import PhoneVerification
from bazasignup.tasks import (
    task_send_email_verification_code,
    task_send_email_verification_code_again,
    task_process_autoapproval,
    task_post_resubmission
)
from bazasignup.utils import save_bazasignup_activity


SKIPPABLE_INDEXES = [1, 2]


def get_current_completed_steps(request, current_step):
    try:
        signup = BazaSignup.objects.get(
            user=request.user)
        completed_steps = signup.get_completed_steps()
        if current_step not in completed_steps:
            completed_steps.append(current_step)
        return ','.join(completed_steps)
    except BazaSignup.DoesNotExist:
        return "0"


def remove_invalidated_steps(request, current_step):
    try:
        signup = BazaSignup.objects.get(
            user=request.user)
        invalidated_steps = signup.get_invalidated_steps()
        if current_step in invalidated_steps:
            invalidated_steps.remove(current_step)
        if not invalidated_steps:
            task_post_resubmission.delay(signup.id)
        return ",".join(invalidated_steps)
    except BazaSignup.DoesNotExist:
        return ""


def remove_invalidated_fields(request, fields):
    try:
        signup = BazaSignup.objects.get(
            user=request.user)
        invalidated_fields = signup.get_invalidated_fields()
        for field in fields:
            # Extra step because street is defined
            # as street_name in serializer
            if field == 'street_name':
                field = 'street'
            if field in invalidated_fields:
                invalidated_fields.remove(field)
        return ",".join(invalidated_fields)
    except BazaSignup.DoesNotExist:
        return ""


def get_step_response(signup):
    next_step_index = get_next_step_index(
        signup.get_completed_steps(), signup.get_invalidated_steps())
    data = {
        'status': signup.status,
        'completed_steps': signup.get_completed_steps(),
        'invalidated_steps': signup.get_invalidated_steps(),
        'invalidated_fields': signup.get_invalidated_fields(),
        'invalidation_comment':
        signup.bazasignupadditionalinfo.invalidation_comment,
        'handling_staff': {
            'fullname': signup.assigned_to.get_full_name()
            if signup.assigned_to else '',
            'id': signup.assigned_to.id
            if signup.assigned_to else ''
        },
        'is_donor': signup.is_donor,
        'next_step': {
            'index': next_step_index,
            'is_skippable': next_step_index in SKIPPABLE_INDEXES
        }
    }
    return Response(data)


def get_next_step_index(completed_steps, invalidated_steps):
    completed_steps = list(map(lambda x: int(x), completed_steps))
    invalidated_steps = list(map(lambda x: int(x), invalidated_steps))
    next_possible_steps = []
    for i in range(4):
        if i not in completed_steps:
            next_possible_steps.append(i)
    if len(invalidated_steps):
        next_possible_steps = invalidated_steps
    return min(next_possible_steps) if len(next_possible_steps) else None


def get_referral_code(signup):
    if hasattr(signup, 'bazasignupreferralcode'):
        return signup.bazasignupreferralcode.code
    return ''


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
            next_step_index = get_next_step_index(
                signup.get_completed_steps(), signup.get_invalidated_steps())
            data = {
                'status': signup.status,
                'referral_code': get_referral_code(signup),
                'completed_steps': signup.get_completed_steps(),
                'invalidated_steps': signup.get_invalidated_steps(),
                'invalidated_fields': signup.get_invalidated_fields(),
                'invalidation_comment':
                signup.bazasignupadditionalinfo.invalidation_comment,
                'handling_staff': {
                    'fullname': signup.assigned_to.get_full_name()
                    if signup.assigned_to else '',
                    'id': signup.assigned_to.id
                    if signup.assigned_to else ''
                },
                'is_donor': signup.is_donor,
                'next_step': {
                    'index': next_step_index,
                    'is_skippable':
                    next_step_index in SKIPPABLE_INDEXES
                }
            }
        except BazaSignup.DoesNotExist:
            data = {
                'status': 'pending',
                'referral_code': '',
                'completed_steps': [],
                'invalidated_steps': [],
                'invalidated_fields': [],
                'invalidation_comment': '',
                'handling_staff': {
                    'fullname': '',
                    'id': ''
                },
                'is_donor': False,
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

    def __save_baza_signup_address(self, signup, serializer, request):
        bazasignupaddress, created = BazaSignupAddress.objects.get_or_create(
            signup=signup,
            address_type='user_input'
        )
        bazasignupaddress.house_number = \
            serializer.validated_data['house_number']
        bazasignupaddress.street = serializer.validated_data['street_name']
        bazasignupaddress.zip_code = serializer.validated_data['zip_code']
        bazasignupaddress.city = serializer.validated_data['city']
        bazasignupaddress.state = serializer.validated_data['state']
        bazasignupaddress.country = serializer.validated_data['country']
        bazasignupaddress.changed_by = request.user
        bazasignupaddress.save()

    def __save_baza_signup_additional_info(self, signup, serializer, request):
        bazasignupadditionalinfo, created =\
            BazaSignupAdditionalInfo.objects.get_or_create(
                signup=signup
            )
        bazasignupadditionalinfo.birth_date = \
            serializer.validated_data['birthdate']
        bazasignupadditionalinfo.changed_by = request.user
        bazasignupadditionalinfo.save()
        request.user.first_name = serializer.validated_data['first_name']
        request.user.last_name = serializer.validated_data['last_name']
        request.user.save()

    def __get_user_info_tab_data(self, signup):
        try:
            address = signup.addresses.get(address_type='user_input')
            referral_code = \
                signup.referred_by.bazasignup.bazasignupreferralcode.code \
                if signup.referred_by else ''
            return {
                'country': address.country,
                'city': address.city,
                'state': address.state,
                'house_number': address.house_number,
                'street_name': address.street,
                'zip_code': address.zip_code,
                'birthdate': signup.bazasignupadditionalinfo.birth_date,
                'referral_code': referral_code,
                'first_name': signup.user.first_name,
                'last_name': signup.user.last_name
            }
        except ObjectDoesNotExist:
            return dict()

    def get(self, request, format=None):
        try:
            signup = BazaSignup.objects.get(user=request.user)
            return Response(self.__get_user_info_tab_data(signup))
        except BazaSignup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, format=None):
        serializer = UserInfoTabSerializer(data=request.data)
        if serializer.is_valid():
            signup, created = BazaSignup.objects.get_or_create(
                user=request.user
            )
            signup.completed_steps = get_current_completed_steps(request, "0")
            signup.changed_by = request.user
            self.__save_baza_signup_address(signup, serializer, request)
            self.__save_baza_signup_additional_info(
                signup, serializer, request)
            if serializer.validated_data['referral_code']:
                bazasignupreferralcode = BazaSignupReferralCode.objects.get(
                    code=serializer.validated_data['referral_code'])
                signup.referred_by = bazasignupreferralcode.signup.user
            if "0" in signup.get_invalidated_steps():
                signup.invalidated_steps = remove_invalidated_steps(
                    request, "0")
                signup.invalidated_fields = remove_invalidated_fields(
                    request, [i for i in serializer.validated_data.keys()])
            signup.save()
            save_bazasignup_activity(
                signup, 'completed name and address tab', request.user)
            return get_step_response(signup)
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
            signup.changed_by = request.user
            if "1" in signup.get_invalidated_steps():
                signup.invalidated_steps = remove_invalidated_steps(
                    request, "1")
                signup.invalidated_fields = remove_invalidated_fields(
                    request, ['email']
                )
            signup.save()
            save_bazasignup_activity(
                signup, 'skipped email verification', request.user)
            return get_step_response(signup)
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
            return Response({'status': 'ok'})
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
            if "1" in signup.get_invalidated_steps():
                signup.invalidated_steps = remove_invalidated_steps(
                    request, "1")
                signup.invalidated_fields = remove_invalidated_fields(
                    request, ['email']
                )
            signup.changed_by = request.user
            signup.save()
            bazasignupemail, created = BazaSignupEmail.objects.get_or_create(
                email=emailverification.email
            )
            bazasignupemail.signups.add(signup)
            emailverification.delete()
            save_bazasignup_activity(
                signup, 'completed email verification', request.user)
            return get_step_response(signup)
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
                return Response({'status': 'ok'})
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
            signup.changed_by = request.user
            if "2" in signup.get_invalidated_steps():
                signup.invalidated_steps = remove_invalidated_steps(
                    request, "2")
                signup.invalidated_fields = remove_invalidated_fields(
                    request, ['phone']
                )
            signup.save()
            save_bazasignup_activity(
                signup, 'skipped phone verification', request.user)
            return get_step_response(signup)
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
            phone_number = None
            if serializer.validated_data.get('phone_number', None):
                phone_number = serializer.validated_data[
                    'phone_number_dial_code'] + serializer.validated_data[
                        'phone_number']
            signup = BazaSignup.objects.get(
                user=request.user
            )
            task_send_phone_verification_code.delay(
                'bazasignup.BazaSignup',
                signup.id,
                phone_number
            )
            return Response({'status': 'ok'})
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
            signup = phoneverification.content_object
            signup.phone_number = phoneverification.phone_number
            signup.completed_steps = get_current_completed_steps(request, "2")
            if "2" in signup.get_invalidated_steps():
                signup.invalidated_steps = remove_invalidated_steps(
                    request, "2")
                signup.invalidated_fields = remove_invalidated_fields(
                    request, ['phone']
                )
            signup.changed_by = request.user
            signup.save()
            bazasignupphone, created = BazaSignupPhone.objects.get_or_create(
                phone_number=phoneverification.phone_number
            )
            bazasignupphone.signups.add(signup)
            phoneverification.delete()
            save_bazasignup_activity(
                signup, 'completed phone verification', request.user)
            return get_step_response(signup)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            signup.logged_ip_address = request.META.get(
                'HTTP_CF_CONNECTING_IP', '')
            signup.changed_by = request.user
            if "3" in signup.get_invalidated_steps():
                signup.invalidated_steps = remove_invalidated_steps(
                    request, "3")
            signup.save()
            if "3" not in signup.get_invalidated_steps():
                task_process_autoapproval.delay(signup.id)
            save_bazasignup_activity(
                signup, 'uploaded an image', request.user)
            return get_step_response(signup)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ToggleDonorView(views.APIView):
    """
    This api will be used to toggle donor status of a distribution signup
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        try:
            signup = BazaSignup.objects.get(user=request.user)
            signup.is_donor = not signup.is_donor
            signup.save()
            return Response({
                'is_donor': signup.is_donor
            })
        except BazaSignup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
