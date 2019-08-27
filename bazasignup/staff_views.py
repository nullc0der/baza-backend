from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from publicusers.views import get_username, get_avatar_color
from userprofile.views import get_profile_photo

from bazasignup.models import (
    BazaSignup,
    StaffLoginSession
)
from bazasignup.serializers import (
    BazaSignupListSerializer,
    BazaSignupCommentSerializer,
    BazaSignupFormResetSerializer
)
from bazasignup.permissions import (
    IsStaffOfSiteOwnerGroup,
    IsOwnerOfComment
)
from bazasignup.utils import (
    get_signup_data,
    get_signup_profile_data
)
from bazasignup.reset_data import reset_signup_form
from bazasignup.tasks import task_send_invalidation_email_to_user


class BazaSignupListView(views.APIView):
    """
    This API will be used to get all the signups list
    """

    permission_classes = (IsAuthenticated, TokenHasScope,
                          IsStaffOfSiteOwnerGroup, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        datas = []
        signups = BazaSignup.objects.filter(
            assigned_to=request.user).order_by('id')
        for signup in signups:
            data = {
                'id_': signup.id,
                'status': signup.status,
                'fullname': signup.user.get_full_name(),
                'username': get_username(signup.user),
                'user_image_url': get_profile_photo(signup.user),
                'user_avatar_color': get_avatar_color(signup.user)
            }
            datas.append(data)
        serializer = BazaSignupListSerializer(datas, many=True)
        return Response(serializer.data)


class BazaSignupProfileDataView(views.APIView):
    """
    This API will return signup applicants profile info
    """

    permission_classes = (IsAuthenticated, TokenHasScope,
                          IsStaffOfSiteOwnerGroup)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, signup_id, format=None):
        try:
            signup = BazaSignup.objects.get(id=signup_id)
            return Response(get_signup_profile_data(signup))
        except BazaSignup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class BazaSignupDetailsView(views.APIView):
    """
    This API will return signup details data
    """

    permission_classes = (IsAuthenticated, TokenHasScope,
                          IsStaffOfSiteOwnerGroup)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, signup_id, format=None):
        try:
            signup = BazaSignup.objects.get(id=signup_id)
            return Response(get_signup_data(signup))
        except BazaSignup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class BazaSignupCommentsView(views.APIView):
    """
    This view can perform CRUD operations on a baza signup comment
    """

    permission_classes = (IsAuthenticated, TokenHasScope,
                          IsStaffOfSiteOwnerGroup, IsOwnerOfComment)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, signup_id, format=None):
        try:
            signup = BazaSignup.objects.get(id=signup_id)
            serializer = BazaSignupCommentSerializer(
                signup.comments.all(), many=True)
            return Response(serializer.data)
        except BazaSignup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, signup_id, format=None):
        try:
            signup = BazaSignup.objects.get(id=signup_id)
            serializer = BazaSignupCommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(commented_by=request.user, signup=signup)
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except BazaSignup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, signup_id, format=None):
        try:
            signup = BazaSignup.objects.get(id=signup_id)
            comment = signup.comments.get(id=request.data['id'])
            self.check_object_permissions(request, comment)
            serializer = BazaSignupCommentSerializer(
                comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, signup_id, format=None):
        try:
            signup = BazaSignup.objects.get(id=signup_id)
            comment = signup.comments.get(id=request.query_params['id'])
            self.check_object_permissions(request, comment)
            data = {'comment_id': comment.id}
            comment.delete()
            return Response(data)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class BazaSignupResetView(views.APIView):
    """
    This view will provide functionality to reset a signup
    application
    """

    permission_classes = (IsAuthenticated, TokenHasScope,
                          IsStaffOfSiteOwnerGroup, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, signup_id, format=None):
        try:
            signup = BazaSignup.objects.get(id=signup_id)
            serializer = BazaSignupFormResetSerializer(data=request.data)
            if serializer.is_valid():
                reset_signup_form(signup, serializer.data)
                task_send_invalidation_email_to_user.delay(signup.id)
                return Response(get_signup_data(signup))
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except BazaSignup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class StaffBarView(views.APIView):
    """
    This view will return staff bars data
    """

    permission_classes = (IsAuthenticated, TokenHasScope,
                          IsStaffOfSiteOwnerGroup, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def __get_datas(self, request):
        return {
            'staff': {
                'fullname': request.user.get_full_name()
            },
            'pending_application_count':
            request.user.assignedbazasignups.filter(status='pending').count()
        }

    def get(self, request, format=None):
        return Response(self.__get_datas(request))


class StaffLoginLogoutView(views.APIView):
    """
    This view will log in/out a staff from distsignup staff
    side
    """

    permission_classes = (IsAuthenticated, TokenHasScope,
                          IsStaffOfSiteOwnerGroup, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def __login_staff(self, request):
        try:
            latest_session = StaffLoginSession.objects.latest('id')
            if latest_session.logged_out_at:
                StaffLoginSession.objects.create(staff=request.user)
        except StaffLoginSession.DoesNotExist:
            StaffLoginSession.objects.create(staff=request.user)

    def __logout_staff(self, request):
        try:
            latest_session = StaffLoginSession.objects.latest('id')
            latest_session.logged_out_at = now()
            latest_session.save()
        except StaffLoginSession.DoesNotExist:
            pass

    def post(self, request, format=None):
        request_type = request.data['request_type']
        if request_type == 'login':
            self.__login_staff(request)
        if request_type == 'logout':
            self.__logout_staff(request)
        return Response({'status': 'ok'})
