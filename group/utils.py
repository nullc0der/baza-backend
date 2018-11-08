from django.utils.timezone import now

from group.models import BasicGroup


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
        basicgroup.super_admins.add(member)
    else:
        if basicgroup.super_admins.count() != 1:
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
