from django.conf import settings

from rest_framework import views, status
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from bazasignup.models import (
    BazaSignup,
    BazaSignupAddress,
    BazaSignupEmail,
    EmailVerification
)
from bazasignup.serializers import (
    UserInfoTabSerializer,
    EmailSerializer,
    EmailVerificationSerializer,
)
from bazasignup.tasks import (
    task_send_email_verification_code,
    task_send_email_verification_code_again
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
    next_step_index = current_step + 1
    data = {
        'status': signup.status,
        'completed_steps': signup.get_completed_steps(),
        'next_step': {
            'index': next_step_index,
            'is_skippable': next_step_index in SKIPPABLE_INDEXES
        }
    }
    return Response(data)


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
            last_completed_step = max(list(map(
                lambda x: int(x), signup.get_completed_steps())))
            data = {
                'status': signup.status,
                'completed_steps': signup.get_completed_steps(),
                'next_step': {
                    'index': last_completed_step + 1,
                    'is_skippable':
                    last_completed_step + 1 in SKIPPABLE_INDEXES
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
