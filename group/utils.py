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
