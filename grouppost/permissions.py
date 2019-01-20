from rest_framework import permissions
from grouppost.models import PostComment


class IsOwnerOfPostOrModeratorOfGroup(permissions.BasePermission):
    """
    Checks if user is owner of post
    """

    def has_object_permission(self, request, view, obj):
        moderators = obj.basic_group.moderators.all()
        return (
            request.user == obj.creator or request.user in moderators
        )


class IsOwnerOfCommentOrModeratorOfGroup(permissions.BasePermission):
    """
    Checks if user is owner of comment
    """

    def has_object_permission(self, request, view, obj):
        moderators = obj.post.basic_group.moderators.all()
        return (
            request.user == obj.commentor or request.user in moderators
        )


class IsOwnerOfObjectOrModeratorOfGroup(permissions.BasePermission):
    """
    Checks if user is owner of post or comment
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, PostComment):
            moderators = obj.post.basic_group.moderators.all()
        else:
            moderators = obj.basic_group.moderators.all()
        return (
            request.user == obj.commentor or request.user in moderators
        )
