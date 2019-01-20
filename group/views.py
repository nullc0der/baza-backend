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

from notifications.utils import create_user_notification

from group.models import (
    BasicGroup, GroupNotification, JoinRequest, GroupMemberNotification,
    GroupInvite, InviteAccept)
from group.serilaizers import (
    BasicGroupSerializer, GroupMemberSerializer, GroupNotificationSerializer,
    GroupJoinRequestSerializer)
from group.permissions import (
    IsAdminOfGroup, IsMemberOfGroup
)
from group.utils import (
    calculate_subscribed_group, change_user_role, get_serialized_notification,
    get_serialized_platform_user)

from group.tasks import task_create_notification


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
            self.check_object_permissions(request, basicgroup)
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
                notification = serializer.save(
                    creator=request.user,
                    basic_group=basicgroup
                )
                task_create_notification.delay(
                    notification.id, 'groupnotification', basicgroup.id)
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


class GroupSubscribeView(APIView):
    """
    This view will subscribe/unsubscribe user from a group

    * Required logged in user
    """
    permission_classes = (IsAuthenticated, TokenHasScope)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, group_id, format=None):
        try:
            basicgroup = BasicGroup.objects.get(id=group_id)
            if request.data.get('subscribe'):
                basicgroup.subscribers.add(request.user)
                return Response(BasicGroupSerializer(basicgroup, context={
                    'user': request.user
                }).data)
            else:
                basicgroup.subscribers.remove(request.user)
                return Response(BasicGroupSerializer(basicgroup, context={
                    'user': request.user
                }).data)
        except BasicGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class JoinGroupView(APIView):
    """
    View to do join operations on a group

    * Required logged in user
    """
    permission_classes = (IsAuthenticated, TokenHasScope)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def process_join_request(self, basicgroup, user):
        data = {
            'group_id': basicgroup.id,
            'type': 'join'
        }
        if basicgroup.join_status == 'open':
            basicgroup.members.add(user)
            data['success'] = True
            data['members'] = [
                user.profile.username or user.username
                for user in basicgroup.members.all()]
            data['user_permission_set'] =\
                calculate_subscribed_group(basicgroup, user)
        if basicgroup.join_status == 'request':
            joinrequest, created = JoinRequest.objects.get_or_create(
                basic_group=basicgroup,
                user=user
            )
            data['success'] = True
            task_create_notification.delay(
                joinrequest.id, 'joinrequest', basicgroup.id)
        if basicgroup.join_status == 'closed':
            data['success'] = False
            data['message'] =\
                'You can join this group by staff invitation only'
        if basicgroup.join_status == 'invite':
            data['success'] = False
            data['message'] = 'You can join this group by invitation only'
        return data

    def post(self, request, group_id, format=None):
        try:
            basicgroup = BasicGroup.objects.get(id=group_id)
            request_type = request.data.get('type')
            if request_type == 'join':
                if request.user not in basicgroup.banned_members.all():
                    data = self.process_join_request(basicgroup, request.user)
                    return Response(data)
                else:
                    data = {
                        'group_id': basicgroup.id,
                        'type': 'join',
                        'success': False,
                        'message': "You're banned from this group"
                    }
                    return Response(data)
            if request_type == 'cancel':
                joinrequest = JoinRequest.objects.get(
                    basic_group=basicgroup,
                    user=request.user
                )
                joinrequest.delete()
                data = {
                    'group_id': basicgroup.id,
                    'type': 'cancel',
                    'success': True
                }
                return Response(data)
            if request_type == 'leave':
                # If group have single owner
                # don't let the user leave ;p
                only_superadmin = False
                try:
                    joinrequest = JoinRequest.objects.get(
                        basic_group=basicgroup,
                        user=request.user
                    )
                    joinrequest.delete()
                except JoinRequest.DoesNotExist:
                    if request.user in basicgroup.super_admins.all()\
                       and basicgroup.super_admins.count() == 1:
                        only_superadmin = True
                if not only_superadmin:
                    basicgroup.members.remove(request.user)
                    basicgroup.super_admins.remove(request.user)
                    basicgroup.admins.remove(request.user)
                    basicgroup.moderators.remove(request.user)
                    if hasattr(basicgroup, 'emailgroup'):
                        emailgroup = basicgroup.emailgroup
                        emailgroup.users.remove(request.user)
                    data = {
                        'group_id': basicgroup.id,
                        'type': 'leave',
                        'success': True,
                        'members': [
                            user.profile.username or user.username
                            for user in basicgroup.members.all()],
                        'user_permission_set': []
                    }
                    return Response(data)
                else:
                    data = {
                        'group_id': basicgroup.id,
                        'type': 'leave',
                        'success': False,
                        'message': "Sorry you can't leave" +
                                " as you're only owner"
                    }
                    return Response(data)
        except BasicGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class GroupJoinRequestView(APIView):
    """
    This view returns all join request

    * Required:
        * Logged in user
        * Permission set
    """
    permission_classes = (IsAuthenticated, TokenHasScope, IsAdminOfGroup)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, group_id, format=None):
        datas = []
        basicgroup = BasicGroup.objects.get(id=group_id)
        self.check_object_permissions(request, basicgroup)
        joinrequests = basicgroup.joinrequest.filter(approved=False)
        for joinrequest in joinrequests:
            data = {
                'id': joinrequest.id,
                'user': make_user_serializeable(joinrequest.user)
            }
            datas.append(data)
        serializer = GroupJoinRequestSerializer(datas, many=True)
        return Response(serializer.data)

    def post(self, request, group_id, format=None):
        try:
            basicgroup = BasicGroup.objects.get(id=group_id)
            self.check_object_permissions(request, basicgroup)
            joinrequest = JoinRequest.objects.get(
                id=request.data.get('request_id'))
            accept = request.data.get('accept')
            if accept:
                user = joinrequest.user
                basicgroup.members.add(user)
                joinrequest.delete()
                data = {
                    'user': make_user_serializeable(user),
                    'user_permission_set': calculate_subscribed_group(
                        basicgroup, user)
                }
                return Response(data)
            return Response()
        except (BasicGroup.DoesNotExist, JoinRequest.DoesNotExist):
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )


class GroupMemberNotificationView(APIView):
    """
    This view returns all unread group notification
    for the member

    * Permission Required:
        * Logged in user
    """

    permission_classes = (IsAuthenticated, TokenHasScope)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, group_id, format=None):
        try:
            datas = []
            basicgroup = BasicGroup.objects.get(id=group_id)
            notifications = GroupMemberNotification.objects.filter(
                basic_group=basicgroup,
                user=request.user,
                read=False
            )
            for notification in notifications:
                data = get_serialized_notification(notification)
                if data:
                    datas.append(data)
            return Response(datas)
        except BasicGroup.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, group_id, format=None):
        try:
            notification_id = request.data.get('id', None)
            notification = GroupMemberNotification.objects.get(
                id=notification_id
            )
            if notification.user == request.user:
                notification.read = True
                notification.save()
                for mainfeed in notification.mainfeed.all():
                    mainfeed.read = True
                    mainfeed.save()
                return Response()
            return Response(status=status.HTTP_403_FORBIDDEN)
        except GroupMemberNotification.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )


class InviteMemberView(APIView):
    """
    * Permission Required
        * Logged in user
        * member of group
    """

    permission_classes = (IsAuthenticated, TokenHasScope, IsMemberOfGroup)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, group_id, format=None):
        """
        This method returns all platform user except member of
        group if the requested user is a member or admin(This
        depends on join_status) of the group
        """
        try:
            basicgroup = BasicGroup.objects.get(id=group_id)
            self.check_object_permissions(request, basicgroup)
            group_staffs = set(
                basicgroup.super_admins.all() |
                basicgroup.admins.all() |
                basicgroup.staffs.all())
            group_members = set(
                basicgroup.super_admins.all() |
                basicgroup.admins.all() |
                basicgroup.moderators.all() |
                basicgroup.staffs.all() |
                basicgroup.members.all())
            if basicgroup.join_status == 'invite'\
                    or basicgroup.join_status == 'open'\
                    and request.user in group_members:
                searchstring = request.GET.get('query', None)
                datas = get_serialized_platform_user(basicgroup, searchstring)
                return Response(datas)
            if basicgroup.join_status == 'closed'\
                    or basicgroup.join_status == 'request'\
                    and request.user in group_staffs:
                searchstring = request.GET.get('query', None)
                datas = get_serialized_platform_user(basicgroup, searchstring)
                return Response(datas)
            return Response(
                status=status.HTTP_403_FORBIDDEN
            )
        except BasicGroup.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, group_id, format=None):
        try:
            basicgroup = BasicGroup.objects.get(id=group_id)
            self.check_object_permissions(request, basicgroup)
            group_staffs = set(
                basicgroup.super_admins.all() |
                basicgroup.admins.all() |
                basicgroup.staffs.all())
            group_members = set(
                basicgroup.super_admins.all() |
                basicgroup.admins.all() |
                basicgroup.moderators.all() |
                basicgroup.staffs.all() |
                basicgroup.members.all())
            if basicgroup.join_status == 'invite'\
                    or basicgroup.join_status == 'open'\
                    and request.user in group_members:
                receiver = User.objects.get(id=request.data.get('user_id'))
                groupinvite, created = GroupInvite.objects.get_or_create(
                    basic_group=basicgroup,
                    sender=request.user,
                    reciever=receiver
                )
                if created:
                    create_user_notification(receiver, groupinvite)
                return Response(receiver.id)
            if basicgroup.join_status == 'closed'\
                    or basicgroup.join_status == 'request'\
                    and request.user in group_staffs:
                receiver = User.objects.get(id=request.data.get('user_id'))
                groupinvite, created = GroupInvite.objects.get_or_create(
                    basic_group=basicgroup,
                    sender=request.user,
                    reciever=receiver
                )
                if created:
                    create_user_notification(receiver, groupinvite)
                return Response(receiver.id)
            return Response(
                status=status.HTTP_403_FORBIDDEN
            )
        except BasicGroup.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )


class InviteAction(APIView):
    """
    This view is used for accept/deny
    a invitation
    * Permission required
        * Logged in user
    """

    permission_classes = (IsAuthenticated, TokenHasScope)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        try:
            groupinvite = GroupInvite.objects.get(
                id=request.data.get('invite_id'))
            message = "You've denied invite"
            if request.data.get('accepted'):
                groupinvite.basic_group.members.add(groupinvite.reciever)
                inviteaccept = InviteAccept(
                    basic_group=groupinvite.basic_group,
                    sender=groupinvite.sender,
                    user=groupinvite.reciever
                )
                inviteaccept.save()
                task_create_notification.delay(
                    inviteaccept.id, 'inviteaccept',
                    groupinvite.basic_group.id)
                message = "You've accepted invite"
            groupinvite.delete()
            return Response({'message': message})
        except GroupInvite.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )
