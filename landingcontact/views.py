from rest_framework import views, status
from rest_framework.response import Response

from landingcontact.serializers import LandingContactSerializer
from landingcontact.utils import get_recaptcha_response
from landingcontact.tasks import task_send_email_to_site_owner


class LandingContactView(views.APIView):
    """
    This API will be used for saving contact message from
    landing page and forwarding this to site owners
    """

    def post(self, request, format=None):
        serializer = LandingContactSerializer(data=request.data)
        if serializer.is_valid():
            response = get_recaptcha_response(
                serializer.validated_data['token'])
            if response:
                if response['success'] and response['score'] > 0.7\
                        and response['action'] == 'contact_form':
                    landingcontact = serializer.save()
                    task_send_email_to_site_owner.delay(landingcontact.id)
            return Response()
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST)
