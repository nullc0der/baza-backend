from django.conf import settings

from rest_framework import viewsets
from rest_framework import status
from rest_framework import parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from group.models import BasicGroup
from group.permissions import IsMemberOfGroup
from groupnews.permissions import IsEditorOfGroup, get_editors
from groupnews.serializers import NewsSerializer, NewsImageSerializer
from groupnews.models import GroupNews


class NewsViewSets(viewsets.ViewSet):
    """
    API viewsets for group news feature
    """
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get_permissions(self):
        permission_classes = (IsAuthenticated, TokenHasScope, IsMemberOfGroup)
        if self.action == 'update' or self.action == 'destroy'\
                or self.action == 'partial_update' or self.action == 'create':
            permission_classes = (
                IsAuthenticated, TokenHasScope, IsEditorOfGroup
            )
        return [permission() for permission in permission_classes]

    def list(self, request):
        try:
            basicgroup = BasicGroup.objects.get(
                id=request.query_params.get('group_id'))
            self.check_object_permissions(request, basicgroup)
            if request.user in get_editors(basicgroup):
                queryset = basicgroup.news.all().order_by('-id')
            else:
                queryset = basicgroup.news.filter(
                    is_published=True).order_by('-id')
            serializer = NewsSerializer(queryset, many=True)
            return Response(serializer.data)
        except BasicGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            basicgroup = BasicGroup.objects.get(
                id=request.data.get('group_id'))
            self.check_object_permissions(request, basicgroup)
            serializer = NewsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(editor=request.user, basic_group=basicgroup)
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        except BasicGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        try:
            news = GroupNews.objects.get(id=pk)
            self.check_object_permissions(request, news.basic_group)
            return Response(
                NewsSerializer(news).data
            )
        except GroupNews.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        try:
            news = GroupNews.objects.get(id=pk)
            self.check_object_permissions(request, news.basic_group)
            serializer = NewsSerializer(news, request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        except GroupNews.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        try:
            news = GroupNews.objects.get(id=pk)
            self.check_object_permissions(request, news.basic_group)
            serializer = NewsSerializer(news, request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        except GroupNews.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            news = GroupNews.objects.get(id=pk)
            self.check_object_permissions(request, news.basic_group)
            data = {'news_id': news.id}
            news.delete()
            return Response(data)
        except GroupNews.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class SiteOwnerGroupNewsViewSets(viewsets.ViewSet):
    """
    This viewsets will return news for landing site
    """

    def list(self, request):
        try:
            site_owner_group = BasicGroup.objects.get(
                is_site_owner_group=True)
            news = site_owner_group.news.filter(
                is_published=True).order_by('-id')
            return Response(NewsSerializer(news, many=True).data)
        except BasicGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        try:
            news = GroupNews.objects.get(id=pk)
            if news.basic_group.is_site_owner_group and news.is_published:
                return Response(NewsSerializer(news).data)
            return Response(status=status.HTTP_403_FORBIDDEN)
        except GroupNews.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class UploadImage(APIView):
    """
    This view saves an image for news

    * Permissions Required
        * Logged in user
        * Permission higher than member role in Group
    """
    permission_classes = (IsAuthenticated, TokenHasScope, IsEditorOfGroup)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']
    parser_classes = (
        parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser)

    def post(self, request, format=None):
        if request.data.get('image'):
            imageserializer = NewsImageSerializer(data=request.data)
            if imageserializer.is_valid():
                newsimage = imageserializer.save(
                    uploader=request.user
                )
                return Response({'image_url': newsimage.image.url})
        return Response()
