from django.conf import settings

from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope
from userprofile.serializers import UserSerializer


class WhoAmI(views.APIView):
    """
    This API returns request.user data
    * datas
        * id
        * username
        * first_name
        * last_name
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        data = UserSerializer(request.user).data
        return Response(data)
