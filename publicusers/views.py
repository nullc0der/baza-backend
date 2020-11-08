from django.conf import settings
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from publicusers.serializers import UserSerializer
from userprofile.utils import get_profile_photo


def get_username(user):
    if hasattr(user, 'profile'):
        return user.profile.username or user.username
    return user.username


def get_avatar_color(user):
    if hasattr(user, 'profile'):
        return user.profile.default_avatar_color
    return '#000000'


def make_user_serializeable(user):
    data = {
        'id': user.id,
        'username': get_username(user),
        'fullname': user.get_full_name(),
        'user_image_url': get_profile_photo(user),
        'user_avatar_color': get_avatar_color(user)
    }
    return data


class UsersListView(APIView):
    """
    View to return all members and staff

    * Only logged in users will be able to access this view
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        """
        Returns list of members and staff excluding request.user
        and AnonymousUser
        """
        datas = []
        users = User.objects.exclude(
            username__in=['AnonymousUser', request.user.username, 'system']
        )
        for user in users:
            data = make_user_serializeable(user)
            datas.append(data)
        serializer = UserSerializer(datas, many=True)
        return Response(serializer.data)
