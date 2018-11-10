from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import User

from rest_framework import status, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from publicusers.views import make_user_serializeable

from group.models import (BasicGroup, GroupNotification)
from group.serilaizers import (
    BasicGroupSerializer, GroupMemberSerializer, GroupNotificationSerializer)
from group.permissions import (
    IsAdminOfGroup, IsMemberOfGroup
)
from group.utils import (
    calculate_subscribed_group, change_user_role)


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


class SiteOwnerGroupView(APIView):
    """
    This view returns the site owner group
    details

    * Required logged in user
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        site_owner_group = BasicGroup.objects.filter(is_site_owner_group=True)
        if len(site_owner_group):
            return Response(BasicGroupSerializer(site_owner_group[0], context={
                'user': request.user
            }).data)
        return Response()


class GroupMembersView(APIView):
    """
    This view returns all members in group with
    their role

    * Required logged in user
    * Permission Required
        * Member role
    """
    permission_classes = (IsAuthenticated, TokenHasScope, IsMemberOfGroup)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, group_id, format=None):
        try:
            datas = []
            basicgroup = BasicGroup.objects.get(id=group_id)
            self.check_object_permissions(request, basicgroup)
            members = basicgroup.super_admins.all() |\
                basicgroup.admins.all() |\
                basicgroup.moderators.all() |\
                basicgroup.staffs.all() |\
                basicgroup.members.all()
            for member in set(members):
                data = {}
                data['user'] = make_user_serializeable(member)
                data['user_permission_set'] = calculate_subscribed_group(
                    basicgroup, member)
                datas.append(data)
            serializer = GroupMemberSerializer(datas, many=True)
            return Response(serializer.data)
        except BasicGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class GroupMemberChangeRoleView(APIView):
    """
    This view changes groups member roles

    * Required:
        * Logged in user
        * Permission set (TODO: Decide permission set)
    * Returns:
        * user: Member data
        * user_permission_set: Member roles
    """
    permission_classes = (IsAuthenticated, TokenHasScope, IsAdminOfGroup)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, group_id, format=None):
        try:
            basicgroup = BasicGroup.objects.get(id=group_id)
            self.check_object_permissions(request, basicgroup)
            member = User.objects.get(id=request.data['member_id'])
            user_permission_set = request.data.get('user_permission_set', None)
            change_user_role(
                basicgroup, member, user_permission_set, request.user)
            data = {
                'user_permission_set': calculate_subscribed_group(
                    basicgroup, member),
                'user': make_user_serializeable(member)
            }
            return Response(GroupMemberSerializer(data).data)
        except BasicGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class GroupNotificationsView(APIView):
    """
    This view returns all groups notifications
    and let the admin create, update and delete

    * Permission Required:
        * Logged in user
        * Admin role for Create, Update and Delete

    """
    permission_classes = (IsAuthenticated, TokenHasScope, IsAdminOfGroup)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, group_id, format=None):
        try:
            basicgroup = BasicGroup.objects.get(id=group_id)
            serializer = GroupNotificationSerializer(
                basicgroup.notifications.all().order_by('-id'),
                many=True
            )
            return Response(
                serializer.data
            )
        except BasicGroup.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, group_id, format=None):
        try:
            basicgroup = BasicGroup.objects.get(id=group_id)
            self.check_object_permissions(request, basicgroup)
            serializer = GroupNotificationSerializer(
                data=request.data
            )
            if serializer.is_valid():
                serializer.save(
                    creator=request.user,
                    basic_group=basicgroup
                )
                return Response(
                    serializer.data
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        except BasicGroup.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, group_id, format=None):
        try:
            basicgroup = BasicGroup.objects.get(id=group_id)
            self.check_object_permissions(request, basicgroup)
            notification = GroupNotification.objects.get(
                id=request.data.get('id'))
            serializer = GroupNotificationSerializer(
                notification,
                data=request.data
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        except BasicGroup.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, group_id, format=None):
        try:
            basicgroup = BasicGroup.objects.get(id=group_id)
            self.check_object_permissions(request, basicgroup)
            notification = GroupNotification.objects.get(
                id=request.query_params.get('id')
            )
            notification_id = notification.id
            notification.delete()
            return Response({'notification_id': notification_id})
        except (BasicGroup.DoesNotExist, GroupNotification.DoesNotExist):
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )
