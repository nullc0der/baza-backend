from rest_framework import permissions


class IsChatRoomSubscriber(permissions.BasePermission):
    """
    Checks if the user is a subscriber of the requested
    Chat Room
    """

    def has_object_permission(self, request, view, obj):
        return request.user in obj.subscribers.all()
