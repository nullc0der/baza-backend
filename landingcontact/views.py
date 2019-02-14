from rest_framework import views, status
from rest_framework.response import Response

from landingcontact.serializers import LandingContactSerializer
from landingcontact.tasks import task_send_email_to_site_owner


class LandingContactView(views.APIView):
    """
    This API will be used for saving contact message from
    landing page and forwarding this to site owners
    """

    def post(self, request, format=None):
        serializer = LandingContactSerializer(data=request.data)
        if serializer.is_valid():
            landingcontact = serializer.save()
            task_send_email_to_site_owner.delay(landingcontact.id)
            return Response()
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST)
