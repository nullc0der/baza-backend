import uuid
from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import User

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from authclient.utils import (
    AuthHelperClient, save_user_auth_data, get_user_auth_data,
    delete_user_auth_data)
from authclient.serializers import (
    LoginSerializer, TwoFactorSerializer, EmailSerializer)

from userprofile.models import UserProfile


URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


def get_login_response(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data.get('username')
        if len(username):
            try:
                username = UserProfile.objects.get(
                    username=username).user.username
            except UserProfile.DoesNotExist:
                pass
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/loginuser/')
        res_status, data = authhelperclient.login_user(
            username,
            serializer.validated_data.get('password')
        )
        if res_status != 200:
            return ({
                'non_field_errors': [data['error_description']]
            }, status.HTTP_400_BAD_REQUEST)
        return ({
            'uuid': '',
            'from_social': False,
            'two_factor_enabled': False,
            'username': data['username'],
            'access_token': data['access_token'],
            'email': data['email'],
            'email_verification': settings.EMAIL_VERIFICATION,
            'email_verified': data['email_verified'],
            'expires_in': now() + timedelta(seconds=data['expires_in'])
        }, status.HTTP_200_OK)
    return (serializer.errors, status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    def post(self, request, format=None):
        data, status = get_login_response(request)
        if status == 200:
            try:
                user = User.objects.get(username=data['username'])
                if hasattr(user, 'two_factor'):
                    if user.two_factor.enabled:
                        data['uuid'] = str(uuid.uuid4())
                        save_user_auth_data(data)
                        data['access_token'] = ''
                        data['expires_in'] = ''
                        data['two_factor_enabled'] = True
                return Response(data, status)
            except User.DoesNotExist:
                pass
        return Response(data, status)


class TwoFactorView(views.APIView):
    def post(self, request, format=None):
        data = get_user_auth_data(request.data['uuid'])
        if data:
            user = User.objects.get(username=data['username'])
            serializer = TwoFactorSerializer(data=request.data, context={
                'user': user
            })
            if serializer.is_valid():
                delete_user_auth_data(request.data['uuid'])
                return Response(data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'non_field_errors':
                ['Something went wrong! Please try to login again']
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(views.APIView):
    def post(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/o/revoke_token/')
        res_status = authhelperclient.logout_user(
            request.data.get('access_token')
        )
        if res_status != 200:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


class RegisterView(views.APIView):
    def post(self, request, format=None):
        if settings.REGISTRATION_ENABLED:
            authhelperclient = AuthHelperClient(
                URL_PROTOCOL +
                settings.CENTRAL_AUTH_INTROSPECT_URL +
                '/authhelper/registeruser/')
            res_status, data = authhelperclient.register_user(
                username=request.data.get('username'),
                password=request.data.get('password'),
                password1=request.data.get('password1'),
                email=request.data.get('email')
            )
            if res_status != 200:
                data['is_registration_enabled'] = settings.REGISTRATION_ENABLED
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'status': 'success',
                'email_verification': settings.EMAIL_VERIFICATION,
                'is_registration_enabled': settings.REGISTRATION_ENABLED
            })
        return Response({
            'is_registration_enabled': settings.REGISTRATION_ENABLED
        })


class ValidateEmailView(views.APIView):
    def post(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/validateemail/')
        res_status, data = authhelperclient.validate_email(
            request.data.get('validation_key'))
        if res_status != 200:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)


class CheckEmailVerifiedView(views.APIView):
    def post(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/isemailverified/'
        )
        res_status, data = authhelperclient.check_email_verified(
            request.data.get('access_token')
        )
        if res_status != 200:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)


class InitiateForgotPasswordView(views.APIView):
    def post(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/initiateforgotpassword/'
        )
        res_status, data = authhelperclient.initate_forgot_password_flow(
            request.data.get('email')
        )
        if res_status != 200:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)


class ForgotPasswordView(views.APIView):
    def post(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/forgotpassword/'
        )
        res_status, data = authhelperclient.reset_user_password(
            request.data.get('password'),
            request.data.get('password1'),
            request.data.get('reset_token')
        )
        if res_status != 200:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)


def get_convert_token_response(request):
    authhelperclient = AuthHelperClient(
        URL_PROTOCOL +
        settings.CENTRAL_AUTH_INTROSPECT_URL +
        '/authhelper/converttoken/'
    )
    res_status, data = authhelperclient.convert_social_user_token(
        request.data.get('token'),
        request.data.get('backend').lower()
    )
    if res_status == 200 and data['access_token_exist']:
        return ({
            'uuid': '',
            'from_social': True,
            'two_factor_enabled': False,
            'username': data['username'],
            'access_token': data['access_token'],
            'email': data['email'],
            'email_verification': settings.EMAIL_VERIFICATION,
            'email_verified': data['email_verified'],
            'expires_in': now() + timedelta(seconds=data['expires_in']),
            'email_exist': data['email_exist']
        }, status.HTTP_200_OK)
    if res_status == 401 and \
            data['error_description'].split(':')[0] == 'email_associated':
        return (
            {'non_field_errors': [
                'The fetched email id %s is associated with another'
                ' account, if you own that account please connect'
                ' this social id from profile section instead'
                % data['error_description'].split(':')[1]
            ]}, status.HTTP_400_BAD_REQUEST
        )
    if res_status == 403:
        return (
            {'non_field_errors': [data['error_description']]},
            status.HTTP_400_BAD_REQUEST)
    return (
        {'non_field_errors': ['Unknown errors occured!']},
        status.HTTP_400_BAD_REQUEST
    )


class ConvertTokenView(views.APIView):
    def post(self, request, format=None):
        data, status = get_convert_token_response(request)
        if status == 200:
            try:
                user = User.objects.get(username=data['username'])
                if hasattr(user, 'two_factor'):
                    if user.two_factor.enabled:
                        data['uuid'] = str(uuid.uuid4())
                        save_user_auth_data(data)
                        data['access_token'] = ''
                        data['expires_in'] = ''
                        data['two_factor_enabled'] = True
                return Response(data, status)
            except User.DoesNotExist:
                pass
        return Response(data, status)


class AddUserEmailView(views.APIView):
    def post(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/addemail/'
        )
        res_status, data = authhelperclient.add_user_email(
            request.data.get('email'),
            request.data.get('access_token')
        )
        if res_status != 200:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)


class GetTwitterRequestCode(views.APIView):
    def post(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/twitter/getrequesttoken/'
        )
        res_status, data = authhelperclient.get_twitter_request_code()
        return Response(data, res_status)


class GetTwitterUserToken(views.APIView):
    def post(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/twitter/getusertoken/'
        )
        res_status, data = authhelperclient.get_twitter_user_token(
            request.query_params['oauth_token'],
            request.query_params['oauth_verifier']
        )
        if res_status == 200:
            request.data['token'] = 'oauth_token=%s&oauth_token_secret=%s' % (
                data['oauth_token'], data['oauth_token_secret'])
            request.data['backend'] = 'twitter'
            data, status = get_convert_token_response(request)
            if status == 200:
                try:
                    user = User.objects.get(username=data['username'])
                    if hasattr(user, 'two_factor'):
                        if user.two_factor.enabled:
                            data['uuid'] = str(uuid.uuid4())
                            save_user_auth_data(data)
                            data['access_token'] = ''
                            data['expires_in'] = ''
                            data['two_factor_enabled'] = True
                    return Response(data, status)
                except User.DoesNotExist:
                    pass
            return Response(data, status)
        return Response(res_status)


class ResendEmailValidationView(views.APIView):
    """
    This api will be used to resend email validation for specified
    email id
    """

    def post(self, request, format=None):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            authhelperclient = AuthHelperClient(
                URL_PROTOCOL +
                settings.CENTRAL_AUTH_INTROSPECT_URL +
                '/authhelper/resendvalidationemail/'
            )
            res_status, data = authhelperclient.resend_email_validation(
                serializer.validated_data.get('email')
            )
            return Response(status=res_status)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def check_registration_enabled(request):
    return Response({
        'is_registration_enabled': settings.REGISTRATION_ENABLED
    })
