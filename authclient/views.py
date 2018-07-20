from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now

from rest_framework import views, status
from rest_framework.response import Response

from authclient.utils import AuthHelperClient
from authclient.serializers import LoginSerializer


URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


class LoginView(views.APIView):
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            authhelperclient = AuthHelperClient(
                URL_PROTOCOL +
                settings.CENTRAL_AUTH_INTROSPECT_URL +
                '/authhelper/loginuser/')
            res_status, data = authhelperclient.login_user(
                serializer.validated_data.get('username'),
                serializer.validated_data.get('password')
            )
            if res_status != 200:
                return Response({
                    'non_field_errors': [data['error_description']]
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'access_token': data['access_token'],
                'email': data['email'],
                'email_verification': settings.EMAIL_VERIFICATION,
                'email_verified': data['email_verified'],
                'expires_in': now() + timedelta(seconds=data['expires_in'])
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'status': 'success',
            'email_verification': settings.EMAIL_VERIFICATION
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
        return Response({
            'access_token': data['access_token'],
            'email': data['email'],
            'email_verification': settings.EMAIL_VERIFICATION,
            'email_verified': data['email_verified'],
            'expires_in': now() + timedelta(seconds=data['expires_in']),
            'email_exist': data['email_exist']
        })
    if res_status == 401 and \
            data['error_description'].split(':')[0] == 'email_associated':
        return Response(
            {'non_field_errors': [
                'The fetched email id %s is associated with another'
                ' account, if you own that account please connect'
                ' this social id from profile section instead'
                % data['error_description'].split(':')[1]
            ]},
            status=status.HTTP_400_BAD_REQUEST
        )
    if res_status == 403:
        return Response({'non_field_errors': [data['error_description']]},
                        status=status.HTTP_400_BAD_REQUEST)
    return Response(
        {'non_field_errors': ['Unknown errors occured!']},
        status=status.HTTP_400_BAD_REQUEST
    )


class ConvertTokenView(views.APIView):
    def post(self, request, format=None):
        return get_convert_token_response(request)


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
            return get_convert_token_response(request)
        return Response(res_status)
