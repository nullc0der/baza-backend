from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now

from rest_framework import status, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from group.models import BasicGroup
from group.serilaizers import BasicGroupSerializer
from group.permissions import (
    IsAdminOfGroup
)


class GroupsView(APIView):
    """
    This view returns all groups list

    * Required logged in user
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        basicgroups = BasicGroup.objects.exclude(
            blocked_members__username__contains=request.user.username
        )
        serializer = BasicGroupSerializer(basicgroups, many=True, context={
            'user': request.user
        })
        return Response(serializer.data)


class GroupDetailView(APIView):
    """
    This view returns specified group detail

    * Required logged in user
    """
    permission_classes = (IsAuthenticated, TokenHasScope, IsAdminOfGroup)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']
    parser_classes = (
        parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser)

    def get(self, request, group_id, format=None):
        try:
            basicgroup = BasicGroup.objects.get(id=group_id)
            return Response(BasicGroupSerializer(basicgroup, context={
                'user': request.user
            }).data)
        except BasicGroup.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, group_id, format=None):
        try:
            basicgroup = BasicGroup.objects.get(id=group_id)
            self.check_object_permissions(request, basicgroup)
            serializer = BasicGroupSerializer(
                data=request.data, instance=basicgroup, partial=True, context={
                    'user': request.user
                })
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except BasicGroup.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, group_id, format=None):
        try:
            basicgroup = BasicGroup.objects.get(id=group_id)
            self.check_object_permissions(request, basicgroup)
            if not basicgroup.flagged_for_deletion:
                basicgroup.flagged_for_deletion = True
                basicgroup.flagged_for_deletion_on = now() + timedelta(days=30)
                basicgroup.save()
            return Response(BasicGroupSerializer(basicgroup, context={
                'user': request.user
            }).data)
        except BasicGroup.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )


class CreateGroupView(APIView):
    """
    This view is used for creating a group for
    requesting user

    * Required logged in user
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        serializer = BasicGroupSerializer(
            data=request.data, partial=True, context={
                'user': request.user
            })
        if serializer.is_valid():
            basicgroup = serializer.save()
            return Response(BasicGroupSerializer(basicgroup, context={
                'user': request.user
            }).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
