from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from notifications.models import Notification
from notifications.utils import get_serialized_notification


class NotificationView(APIView):
    """
    This view returns list of unread notifications of
    request.user

    * Permission required:
        * Logged in user
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        datas = []
        notifications = Notification.objects.filter(
            user=request.user,
            read=False
        )
        for notification in notifications:
            data = get_serialized_notification(notification)
            if data:
                datas.append(data)
        return Response(datas)


class NotificationDetailView(APIView):
    """
    This view makes a notification or list of notifications
    read/unread
    * Permission required
        * Logged in user
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        id_lists = request.data.get('idlist', None)
        processed_ids = []
        for notification_id in id_lists:
            try:
                notification = Notification.objects.get(id=notification_id)
                if notification.user == request.user:
                    notification.read = True
                    if hasattr(notification.content_object, 'read'):
                        notification.content_object.read = True
                        notification.content_object.save()
                    notification.save()
                    processed_ids.append(notification_id)
            except Notification.DoesNotExist:
                pass
        return Response(processed_ids)
