from rest_framework import permissions

from group.models import BasicGroup


class IsStaffOfSiteOwnerGroup(permissions.BasePermission):
    """
    This permission checks if the request.user is a staff of
    site owner group or not
    """
    message = "Nice try, but you need to be staff to perform this action"

    def has_permission(self, request, view):
        site_owner_group = BasicGroup.objects.filter(is_site_owner_group=True)
        if len(site_owner_group):
            return request.user in site_owner_group[0].staffs.all()
        return False
