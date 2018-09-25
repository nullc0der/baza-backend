from django.conf import settings

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import (
    FormParser, MultiPartParser, JSONParser)

from oauth2_provider.contrib.rest_framework import TokenHasScope

from userprofile.models import (
    UserDocument, UserPhoto, UserProfilePhoto)
from userprofile.serializers import (
    UserProfileSerializer, UserDocumentSerializer,
    UserPhotoSerializer, UserProfilePhotoSerializer)


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
            return Response(UserProfileSerializer(profile).data)
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
