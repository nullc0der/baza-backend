from django.utils.timezone import now

from group.models import BasicGroup


def process_flagged_for_delete_group():
    for basicgroup in BasicGroup.objects.all():
        if basicgroup.flagged_for_deletion\
                and basicgroup.flagged_for_deletion_on < now():
            basicgroup.delete()
