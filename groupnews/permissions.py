from rest_framework import permissions


def get_editors(obj):
    return set(
        obj.super_admins.all() |
        obj.admins.all() |
        obj.staffs.all() |
        obj.moderators.all()
    )


class IsEditorOfGroup(permissions.BasePermission):
    """
    Checks if user is an editor of the group
    """

    def has_object_permission(self, request, view, obj):
        editors = get_editors(obj)
        return request.user in editors
