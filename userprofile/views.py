from django.conf import settings

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import (
    FormParser, MultiPartParser, JSONParser)

from oauth2_provider.contrib.rest_framework import TokenHasScope

from authclient.utils import AuthHelperClient
from userprofile.models import (
    UserDocument, UserPhoto, UserProfilePhoto, UserPhone)
from userprofile.serializers import (
    UserProfileSerializer, UserDocumentSerializer,
    UserPhotoSerializer, UserProfilePhotoSerializer,
    UserPhoneSerializer)


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
