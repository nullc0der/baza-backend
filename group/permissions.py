from rest_framework import permissions
from grouppost.models import GroupPost, PostComment


class IsAdminOfGroup(permissions.BasePermission):
    """
    Checks if user is admin of the group
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, GroupPost):
            obj = obj.basic_group
        if isinstance(obj, PostComment):
            obj = obj.post.basic_group
        return request.user in set(
            obj.super_admins.all() |
            obj.admins.all()
        )


class IsModeratorOfGroup(permissions.BasePermission):
    """
    Checks if user is moderator of the group
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, GroupPost):
            obj = obj.basic_group
        if isinstance(obj, PostComment):
            obj = obj.post.basic_group
        return request.user in obj.moderators.all()


class IsMemberOfGroup(permissions.BasePermission):
    """
    checks if user is member of the group
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, GroupPost):
            obj = obj.basic_group
        if isinstance(obj, PostComment):
            obj = obj.post.basic_group
        return request.user in set(
            obj.super_admins.all() |
            obj.admins.all() |
            obj.staffs.all() |
            obj.moderators.all() |
            obj.members.all()
        )
