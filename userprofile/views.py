from rest_framework import views
from rest_framework.response import Response
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
    def get(self, request, format=None):
        data = UserSerializer(request.user).data
        return Response(data)
