from django.conf import settings
from rest_framework import views, status
from rest_framework.response import Response

from authclient.utils import AuthHelperClient
from authclient.serializers import LoginSerializer


URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


class LoginView(views.APIView):
    """
    TODO: Add documentation
    """

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
                'email_verification': settings.EMAIL_VERIFICATION,
                'email_verified': data['email_verified']
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(views.APIView):
    """
    TODO: Add documentation
    """

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
    """
    TODO: Add documentation
    """

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
    """
    TODO: Add documentation
    """

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
    """
    TODO: Add documentation
    """

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
    """
    TODO: Add documentation
    """

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
    """
    TODO: Add documentation
    """

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
