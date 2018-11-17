from django.utils.timezone import now
from django.db.models import Q

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from userprofile.models import UserProfile
from publicusers.views import make_user_serializeable
from group.models import (
    BasicGroup, JoinRequest, GroupMemberNotification,
    GroupNotification, InviteAccept
)

channel_layer = get_channel_layer()


def process_flagged_for_delete_group():
    for basicgroup in BasicGroup.objects.all():
        if basicgroup.flagged_for_deletion\
                and basicgroup.flagged_for_deletion_on < now():
            basicgroup.delete()


def calculate_subscribed_group(basicgroup, member):
    subscribed_groups = []
    if member in basicgroup.subscribers.all():
        subscribed_groups.append(101)
    if member in basicgroup.members.all():
        subscribed_groups.append(102)
    if member in basicgroup.super_admins.all():
        subscribed_groups.append(103)
    if member in basicgroup.admins.all():
        subscribed_groups.append(104)
    if member in basicgroup.moderators.all():
        subscribed_groups.append(105)
    if member in basicgroup.staffs.all():
        subscribed_groups.append(106)
    if member in basicgroup.banned_members.all():
        subscribed_groups.append(107)
    if member in basicgroup.blocked_members.all():
        subscribed_groups.append(108)
    return subscribed_groups


def remove_user_from_role(basicgroup, member):
    basicgroup.super_admins.remove(member)
    basicgroup.admins.remove(member)
    basicgroup.staffs.remove(member)
    basicgroup.moderators.remove(member)
    basicgroup.members.remove(member)
    basicgroup.subscribers.remove(member)


def change_user_role(basicgroup, member, subscribed_groups, editor):
    if 101 in subscribed_groups:
        basicgroup.subscribers.add(member)
    else:
        basicgroup.subscribers.remove(member)
    if 102 in subscribed_groups:
        basicgroup.members.add(member)
    else:
        basicgroup.members.remove(member)
    if 103 in subscribed_groups:
        if editor in basicgroup.super_admins.all():
            basicgroup.super_admins.add(member)
    else:
        if basicgroup.super_admins.count() != 1 and\
                editor in basicgroup.super_admins.all():
            basicgroup.super_admins.remove(member)
    if 104 in subscribed_groups:
        basicgroup.admins.add(member)
    else:
        basicgroup.admins.remove(member)
    if 105 in subscribed_groups:
        basicgroup.moderators.add(member)
    else:
        basicgroup.moderators.remove(member)
    if 106 in subscribed_groups:
        basicgroup.staffs.add(member)
    else:
        basicgroup.staffs.remove(member)
    if 107 in subscribed_groups:
        if member != editor:
            basicgroup.banned_members.add(member)
            remove_user_from_role(basicgroup, member)
    else:
        basicgroup.banned_members.remove(member)
    if 108 in subscribed_groups:
        if member != editor:
            basicgroup.blocked_members.add(member)
            remove_user_from_role(basicgroup, member)
    else:
        basicgroup.blocked_members.remove(member)


def create_notification(objid, objtype, basicgroupid):
    basicgroup = BasicGroup.objects.get(id=basicgroupid)
    if objtype == 'joinrequest':
        obj = JoinRequest.objects.get(id=objid)
        for admin in set(
                basicgroup.super_admins.all() | basicgroup.admins.all()):
            group_member_notification = GroupMemberNotification(
                basic_group=basicgroup,
                user=admin,
                content_object=obj
            )
            group_member_notification.save()
            websocket_data = {
                'group_id': basicgroup.id,
                'notification': get_serialized_notification(
                    group_member_notification)
            }
            async_to_sync(channel_layer.group_send)(
                'group_notifications_for_%s' % admin.username,
                {
                    'type': 'groupnotification.message',
                    'message': websocket_data
                }
            )
    if objtype == 'groupnotification':
        obj = GroupNotification.objects.get(id=objid)
        for member in set(
                basicgroup.super_admins.all() | basicgroup.admins.all() |
                basicgroup.staffs.all() | basicgroup.moderators.all() |
                basicgroup.members.all()):
            group_member_notification = GroupMemberNotification(
                basic_group=basicgroup,
                user=member,
                content_object=obj
            )
            group_member_notification.save()
            websocket_data = {
                'group_id': basicgroup.id,
                'notification': get_serialized_notification(
                    group_member_notification)
            }
            async_to_sync(channel_layer.group_send)(
                'group_notifications_for_%s' % member.username,
                {
                    'type': 'groupnotification.message',
                    'message': websocket_data
                }
            )
    if objtype == 'inviteaccept':
        obj = InviteAccept.objects.get(id=objid)
        for admin in set(
                basicgroup.super_admins.all() | basicgroup.admins.all()):
            group_member_notification = GroupMemberNotification(
                basic_group=basicgroup,
                user=admin,
                content_object=obj
            )
            group_member_notification.save()
            websocket_data = {
                'group_id': basicgroup.id,
                'notification': get_serialized_notification(
                    group_member_notification)
            }
            async_to_sync(channel_layer.group_send)(
                'group_notifications_for_%s' % admin.username,
                {
                    'type': 'groupnotification.message',
                    'message': websocket_data
                }
            )


def get_serialized_notification(notification):
    data = {}
    if notification.content_object:
        if isinstance(notification.content_object, JoinRequest):
            joinrequest = notification.content_object
            data['type'] = 'joinrequest'
            data['joinrequest_id'] = joinrequest.id
            data['user'] = make_user_serializeable(joinrequest.user)
            data['notification_id'] = notification.id
        if isinstance(notification.content_object, GroupNotification):
            group_notification = notification.content_object
            data['type'] = 'groupnotification'
            data['notification_id'] = notification.id
            data['group_notification_id'] = group_notification.id
            data['notification'] = group_notification.notification
            data['created_on'] = group_notification.created_on.isoformat()
        if isinstance(notification.content_object, InviteAccept):
            group_invite = notification.content_object
            data['type'] = 'inviteaccept'
            data['notification_id'] = notification.id
            data['sender'] = make_user_serializeable(group_invite.sender)
            data['member'] = make_user_serializeable(group_invite.user)
    return data


def get_platform_users(basicgroup, searchstring):
    final_list = []
    group_members = set(
        basicgroup.super_admins.all() |
        basicgroup.admins.all() |
        basicgroup.moderators.all() |
        basicgroup.staffs.all() |
        basicgroup.members.all() |
        basicgroup.banned_members.all() |
        basicgroup.blocked_members.all())
    platform_users = UserProfile.objects.filter(
        Q(username__istartswith=searchstring) |
        Q(user__username__istartswith=searchstring) |
        Q(user__first_name__istartswith=searchstring) |
        Q(user__last_name__istartswith=searchstring)
    )
    for platform_user in platform_users:
        if platform_user not in group_members:
            final_list.append(platform_user)
    return final_list


def get_serialized_platform_user(basicgroup, searchstring):
    datas = []
    platform_users = get_platform_users(basicgroup, searchstring)
    for platform_user in platform_users:
        data = make_user_serializeable(platform_user.user)
        data['is_invited'] = False
        for invite in platform_user.user.received_invites.all():
            if invite.basic_group == basicgroup:
                data['is_invited'] = True
        datas.append(data)
    return datas
