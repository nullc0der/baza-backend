import os
import json

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from groupfaq.serializers import FaqJSONUploadSerializer


class UploadFaqJSON(views.APIView):
    """
    This view will be used to upload FAQ json
    file
    """
    parser_classes = (FormParser, MultiPartParser, )

    def post(self, request, format=None):
        serializer = FaqJSONUploadSerializer(data=request.data)
        if serializer.is_valid():
            file_name = os.path.join(
                settings.MEDIA_ROOT, 'faqjson') + '/faq.json'
            if os.path.isfile(file_name):
                os.remove(file_name)
            default_storage.save(file_name, ContentFile(
                serializer.validated_data['faqfile'].read()))
            return Response({'success': 'file saved'})
        return Response(
            serializer.errors, status=status.HTTP_403_FORBIDDEN)


class DownloadFaqJSON(views.APIView):
    """
    This view will be used to download faq data
    """

    def get(self, request, format=None):
        file_name = os.path.join(
            settings.MEDIA_ROOT, 'faqjson') + '/faq.json'
        if os.path.isfile(file_name):
            f = open(file_name, 'r')
            data = json.load(f)
            f.close()
            return Response(data)
        return Response(status=status.HTTP_404_NOT_FOUND)
