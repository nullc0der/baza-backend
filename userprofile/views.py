from django.conf import settings
from django.template import loader
from django.http import HttpResponse
from django.utils.crypto import get_random_string

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import (
    FormParser, MultiPartParser, JSONParser)

from oauth2_provider.contrib.rest_framework import TokenHasScope

from authclient.utils import AuthHelperClient
from userprofile.models import (
    UserDocument, UserPhoto, UserProfilePhoto, UserPhone,
    UserTwoFactor, UserTwoFactorRecovery)
from userprofile.serializers import (
    UserProfileSerializer, UserDocumentSerializer,
    UserPhotoSerializer, UserProfilePhotoSerializer,
    UserPhoneSerializer)
from userprofile.tasks import task_send_two_factor_email


URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


def get_profile_photo(user):
    profile_photo = None
    try:
        profilephoto = user.profile.profilephotos.get(
            is_active=True)
        profile_photo = profilephoto.userphoto.photo.url
    except UserProfilePhoto.DoesNotExist:
        pass
    return profile_photo


class UserProfileView(views.APIView):
    """
    This API is used to get and save user profile details
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user.profile)
        data = serializer.data
        data['profile_photo'] = get_profile_photo(request.user)
        return Response(data)

    def post(self, request, format=None):
        serializer = UserProfileSerializer(
            request.user.profile, data=request.data, partial=True, context={
                'request': request
            })
        if serializer.is_valid():
            profile = serializer.save()
            data = UserProfileSerializer(profile).data
            data['profile_photo'] = get_profile_photo(request.user)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDocumentView(views.APIView):
    """
    This API will return all user documents
    and save/delete user document
    """

    parser_classes = (FormParser, MultiPartParser, JSONParser, )
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        userdocuments = request.user.profile.documents.all()
        serializer = UserDocumentSerializer(userdocuments, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UserDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=request.user.profile)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        try:
            document = UserDocument.objects.get(
                id=request.query_params['document_id'])
            if document.profile == request.user.profile:
                document.delete()
                return Response(request.query_params['document_id'])
            return Response(
                "You can't delete this file",
                status=status.HTTP_400_BAD_REQUEST
            )
        except UserDocument.DoesNotExist:
            return Response(
                "Requested document can't be found",
                status=status.HTTP_404_NOT_FOUND)


class UserPhotoView(views.APIView):
    """
    This API will return all user photos
    and save/delete user photo
    """

    parser_classes = (FormParser, MultiPartParser, JSONParser, )
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        userphotos = request.user.profile.photos.all()
        serializer = UserPhotoSerializer(userphotos, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UserPhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=request.user.profile)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        try:
            photo = UserPhoto.objects.get(id=request.query_params['photo_id'])
            if photo.profile == request.user.profile:
                photo.delete()
                return Response(request.query_params['photo_id'])
            return Response(
                "You can't delete this photo",
                status=status.HTTP_400_BAD_REQUEST
            )
        except UserPhoto.DoesNotExist:
            return Response(
                "Requested photo can't be found",
                status=status.HTTP_404_NOT_FOUND)


class UserProfilePhotoView(views.APIView):
    """
    This view will return all list of user profile photo
    and create/delete/set profile photo
    """

    parser_classes = (FormParser, MultiPartParser, JSONParser, )
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        profilephotos = request.user.profile.profilephotos.all()
        serializer = UserProfilePhotoSerializer(profilephotos, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        userphoto_serializer = UserPhotoSerializer(data=request.data)
        if userphoto_serializer.is_valid():
            userphoto = userphoto_serializer.save(profile=request.user.profile)
            data = {
                'is_active': True
            }
            serializer = UserProfilePhotoSerializer(data=data)
            if serializer.is_valid():
                for userprofilephoto in UserProfilePhoto.objects.filter(
                        profile=request.user.profile):
                    userprofilephoto.is_active = False
                    userprofilephoto.save()
                serializer.save(
                    userphoto=userphoto, profile=request.user.profile)
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(
            userphoto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        try:
            userprofilephoto = UserProfilePhoto.objects.get(
                id=request.query_params['profile_photo_id'])
            if userprofilephoto.profile == request.user.profile:
                userprofilephoto.delete()
                return Response(request.query_params['profile_photo_id'])
            return Response(
                "You can't delete this photo",
                status=status.HTTP_400_BAD_REQUEST)
        except UserProfilePhoto.DoesNotExist:
            return Response(
                "Requested profile photo can't be found",
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, format=None):
        try:
            userprofilephoto = UserProfilePhoto.objects.get(
                id=request.data['profile_photo_id'])
            if request.data['set_active'] and\
                    userprofilephoto.profile == request.user.profile:
                current_actives =\
                    request.user.profile.profilephotos.filter(
                        is_active=True)
                for current_active in current_actives:
                    current_active.is_active = False
                    current_active.save()
                userprofilephoto.is_active = True
                userprofilephoto.save()
                return Response(request.data['profile_photo_id'])
            return Response(
                "You are not authorized",
                status=status.HTTP_400_BAD_REQUEST
            )
        except UserProfilePhoto.DoesNotExist:
            return Response(
                "Requested profile photo can't be found",
                status=status.HTTP_404_NOT_FOUND
            )


class UserPhoneView(views.APIView):
    """
    This view will be used for CRUD of user phone number
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        phones = request.user.profile.phones.all()
        serializer = UserPhoneSerializer(phones, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UserPhoneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=request.user.profile)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        try:
            phone = UserPhone.objects.get(id=request.query_params['id'])
            if phone.profile == request.user.profile:
                phone.delete()
                return Response(request.query_params['id'])
            return Response(
                "You can't delete this phone number",
                status=status.HTTP_400_BAD_REQUEST
            )
        except UserPhone.DoesNotExist:
            return Response(
                "Requested phone number can't be found",
                status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, format=None):
        try:
            phone = UserPhone.objects.get(id=request.data['id'])
            if phone.profile == request.user.profile:
                serializer = UserPhoneSerializer(
                    data=request.data, instance=phone, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                "You can't update this phone number",
                status=status.HTTP_400_BAD_REQUEST
            )
        except UserPhone.DoesNotExist:
            return Response(
                "Requested phone number can't be found",
                status=status.HTTP_400_BAD_REQUEST
            )


class UserEmailView(views.APIView):
    """
    This view will be used to crud user emails
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/useremails/'
        )
        res_status, data = authhelperclient.get_user_emails(
            request.query_params['access_token'])
        return Response(data, res_status)

    def post(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/addemail/'
        )
        res_status, data = authhelperclient.add_user_email(
            request.data.get('email'),
            request.data['access_token'],
            from_social=False
        )
        if res_status != 200:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)

    def delete(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/deleteemail/'
        )
        res_status, data = authhelperclient.delete_or_update_user_email(
            request.query_params['access_token'],
            request.query_params['email_id']
        )
        return Response(data, res_status)

    def put(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/updateemail/'
        )
        res_status, data = authhelperclient.delete_or_update_user_email(
            request.data['access_token'], request.data['email_id'])
        return Response(data, res_status)


class UserSocialView(views.APIView):
    """
    This view will be used to get, connect, disconnect user
    social auth
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def connect_account(self, request):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/connectsocialauth/'
        )
        return authhelperclient.connect_social_auth(
            access_token=request.data['access_token'],
            provider=request.data['provider'],
            provider_access_token=request.data['provider_access_token']
        )

    def disconnect_account(self, request):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/disconnectsocialauth/'
        )
        return authhelperclient.disconnect_social_auth(
            access_token=request.data['access_token'],
            provider=request.data['provider'],
            association_id=request.data['association_id']
        )

    def get(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/getsocialauths/'
        )
        res_status, data = authhelperclient.get_user_social_auths(
            request.query_params['access_token'])
        return Response(data, res_status)

    def post(self, request, format=None):
        if request.data['req_type'] == 'connect':
            res_status, data = self.connect_account(request)
        if request.data['req_type'] == 'disconnect':
            res_status, data = self.disconnect_account(request)
        return Response(data, res_status)


class ConnectTwitterView(views.APIView):
    """
    This view will be used to connect twitter account
    """

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
            authhelperclient = AuthHelperClient(
                URL_PROTOCOL +
                settings.CENTRAL_AUTH_INTROSPECT_URL +
                '/authhelper/connectsocialauth/'
            )
            res_status, data = authhelperclient.connect_social_auth(
                access_token=request.META['HTTP_ACCESS_TOKEN'],
                provider='twitter',
                oauth_token=data['oauth_token'],
                oauth_token_secret=data['oauth_token_secret']
            )
            return Response(data, res_status)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SetUserPasswordView(views.APIView):
    """
    This view will be used to set new password for an user
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/setpassword/'
        )
        res_status, data = authhelperclient.set_user_password(
            access_token=request.data['access_token'],
            current_password=request.data['current_password'],
            new_password_1=request.data['new_password_1'],
            new_password_2=request.data['new_password_2']
        )
        return Response(data, res_status)


class UserTwoFactorView(views.APIView):
    """
    This view will be used to get info about user's
    two factor and set two factor
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get_create_totp_response(self, twofactor):
        return Response({
            'provisioning_uri': twofactor.get_totp_provisioning_uri()
        })

    def get_verify_totp_response(self, twofactor, otp, username, access_token):
        verified = twofactor.verify_totp(otp)
        if verified:
            twofactor.enabled = True
            twofactor.save()
            UserTwoFactorRecovery.objects.filter(
                user=twofactor.user
            ).delete()
            strings = [get_random_string(
                length=6, allowed_chars='0123456789') for i in range(10)]
            for string in strings:
                UserTwoFactorRecovery.objects.create(
                    user=twofactor.user,
                    code=string
                )
            task_send_two_factor_email.delay(
                username, access_token, 0
            )
            return Response({
                'two_factor_enabled': twofactor.enabled
            })
        return Response({
            'two_factor_enabled': twofactor.enabled,
            'error': 'Code invalid'
        }, status=status.HTTP_400_BAD_REQUEST)

    def get_recovery_codes_response(self, user, access_token):
        template = loader.get_template('userprofile/twofactor.txt')
        recovery_codes = user.two_factor_recovery.all()
        text = template.render({
            'site': settings.HOST_URL,
            'twofactorrecoveries': recovery_codes
        })
        task_send_two_factor_email.delay(
            user.profile.username or user.username, access_token, 2
        )
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
            'recovery-codes.txt')
        return response

    def get_disable_two_factor_code_response(self, user, access_token):
        try:
            twofactor = UserTwoFactor.objects.get(
                user=user
            )
            twofactor.delete()
            user.two_factor_recovery.all().delete()
            task_send_two_factor_email.delay(
                user.profile.username or user.username, access_token, 1
            )
        except UserTwoFactor.DoesNotExist:
            pass
        return Response({
            'two_factor_enabled': False
        })

    def get(self, request, format=None):
        if request.query_params['type'] == 'getcodes':
            return self.get_recovery_codes_response(
                request.user,
                request.META['HTTP_AUTHORIZATION'].split(' ')[1]
            )
        two_factor_enabled = False
        try:
            usertwofactor = UserTwoFactor.objects.get(
                user=request.user
            )
            two_factor_enabled = usertwofactor.enabled
        except UserTwoFactor.DoesNotExist:
            pass
        return Response({
            'two_factor_enabled': two_factor_enabled
        })

    def post(self, request, format=None):
        usertwofactor, created = UserTwoFactor.objects.get_or_create(
            user=request.user
        )
        if request.data['type'] == 'verify':
            return self.get_verify_totp_response(
                usertwofactor,
                request.data['otp'],
                request.user.profile.username or request.user.username,
                request.META['HTTP_AUTHORIZATION'].split(' ')[1])
        if request.data['type'] == 'disable':
            authhelperclient = AuthHelperClient(
                URL_PROTOCOL +
                settings.CENTRAL_AUTH_INTROSPECT_URL +
                '/authhelper/checkpassword/'
            )
            res_status, data = authhelperclient.check_user_password(
                request.META['HTTP_AUTHORIZATION'].split(' ')[1],
                request.data['password']
            )
            if data['password_valid']:
                return self.get_disable_two_factor_code_response(
                    request.user,
                    request.META['HTTP_AUTHORIZATION'].split(' ')[1]
                )
            return Response(data, res_status)
        return self.get_create_totp_response(usertwofactor)
