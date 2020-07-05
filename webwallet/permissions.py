from rest_framework import permissions


class IsOwnerOfWallet(permissions.BasePermission):
    """
    Check if the user is owner of the userwebwallet
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
