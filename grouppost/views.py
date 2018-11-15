from django.conf import settings

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from rest_framework import parsers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from group.permissions import (
    IsMemberOfGroup, IsModeratorOfGroup)
from group.models import BasicGroup
from grouppost.models import GroupPost, PostComment
from grouppost.serializers import (
    PostSerializer, CommentSerialzer, PostImageSerializer)
from grouppost.permissions import (
    IsOwnerOfPostOrModeratorOfGroup, IsOwnerOfCommentOrModeratorOfGroup,
    IsOwnerOfObjectOrModeratorOfGroup)


def get_approver_set(basicgroup):
    return set(  # NOTE: not sure why the | needed, research
        basicgroup.super_admins.all() |
        basicgroup.admins.all() |
        basicgroup.staffs.all() |
        basicgroup.moderators.all()
    )


class PostViewSets(viewsets.ViewSet):
    """
    API viewsets for Group Post feature
    """
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get_permissions(self):
        permission_classes = (IsAuthenticated, TokenHasScope, IsMemberOfGroup)
        if self.action == 'update' or self.action == 'destroy':
            permission_classes = (
                IsAuthenticated, TokenHasScope,
                IsOwnerOfPostOrModeratorOfGroup)
        if self.action == 'partial_update':
            permission_classes = (
                IsAuthenticated, TokenHasScope, IsModeratorOfGroup)
        return [permission() for permission in permission_classes]

    def list(self, request):
        try:
            basicgroup = BasicGroup.objects.get(
                id=request.query_params.get('group_id'))
            self.check_object_permissions(request, basicgroup)
            if request.user in get_approver_set(basicgroup):
                queryset = basicgroup.posts.all()
            else:
                queryset = set(basicgroup.posts.filter(approved=True) |
                               basicgroup.posts.filter(creator=request.user))
            serializer = PostSerializer(queryset, many=True)
            return Response(serializer.data)
        except BasicGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            basicgroup = BasicGroup.objects.get(
                id=request.data.get('group_id'))
            self.check_object_permissions(request, basicgroup)
            serializer = PostSerializer(data=request.data)
            if serializer.is_valid():
                if request.user in get_approver_set(basicgroup)\
                        or basicgroup.auto_approve_post:
                    serializer.save(
                        creator=request.user, basic_group=basicgroup,
                        approved=True
                    )
                else:
                    serializer.save(
                        creator=request.user, basic_group=basicgroup
                    )
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except BasicGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        try:
            post = GroupPost.objects.get(id=pk)
            self.check_object_permissions(request, post)
            return Response(
                PostSerializer(post).data
            )
        except GroupPost.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        try:
            post = GroupPost.objects.get(id=pk)
            self.check_object_permissions(request, post)
            serializer = PostSerializer(post, request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        except BasicGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        try:
            post = GroupPost.objects.get(id=pk)
            self.check_object_permissions(request, post)
            serializer = PostSerializer(post, request.data, partial=True)
            if serializer.is_valid():
                serializer.save(
                    approved=True,
                    approved_by=request.user
                )
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        except GroupPost.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            post = GroupPost.objects.get(id=pk)
            self.check_object_permissions(request, post)
            data = {'post_id': post.id}
            post.delete()
            return Response(data)
        except GroupPost.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CommentViewset(viewsets.ViewSet):
    """
    API Viewset for comments
    """
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get_permissions(self):
        permission_classes = (IsAuthenticated, TokenHasScope,
                              IsMemberOfGroup)
        if self.action == 'update':
            permission_classes = (
                IsAuthenticated, TokenHasScope,
                IsOwnerOfCommentOrModeratorOfGroup)
        if self.action == 'partial_update':
            permission_classes = (
                IsAuthenticated, TokenHasScope, IsModeratorOfGroup)
        if self.action == 'destroy':
            permission_classes = (
                IsAuthenticated, TokenHasScope,
                IsOwnerOfObjectOrModeratorOfGroup)
        return [permission() for permission in permission_classes]

    def list(self, request):
        try:
            post = GroupPost.objects.get(
                id=request.query_params.get('post_id'))
            self.check_object_permissions(request, post)
            if request.user in get_approver_set(post.basic_group):
                comments = post.comments.all()
            else:
                comments = set(post.comments.filter(approved=True) |
                               post.comments.filter(commentor=request.user))
            serializer = CommentSerialzer(comments, many=True)
            return Response(serializer.data)
        except GroupPost.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            post = GroupPost.objects.get(id=request.data.get('post_id'))
            self.check_object_permissions(request, post)
            serializer = CommentSerialzer(data=request.data)
            if serializer.is_valid():
                if request.user in get_approver_set(post.basic_group)\
                        or post.basic_group.auto_approve_comment:
                    serializer.save(
                        post=post, commentor=request.user, approved=True
                    )
                else:
                    serializer.save(
                        post=post, commentor=request.user
                    )
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except GroupPost.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        try:
            comment = PostComment.objects.get(id=pk)
            self.check_object_permissions(request, comment)
            serializer = CommentSerialzer(comment, request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PostComment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        try:
            comment = PostComment.objects.get(id=pk)
            self.check_object_permissions(request, comment)
            serializer = CommentSerialzer(comment, request.data, partial=True)
            if serializer.is_valid():
                serializer.save(
                    approved=True,
                    approved_by=request.user
                )
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PostComment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            comment = PostComment.objects.get(id=pk)
            self.check_object_permissions(request, comment)
            data = {'comment_id': comment.id, 'post_id': comment.post.id}
            comment.delete()
            return Response(data)
        except PostComment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class UploadImage(APIView):
    """
    This view saves an image for post

    * Permissions Required
        * Logged in user
    """
    permission_classes = (IsAuthenticated, IsMemberOfGroup)
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']
    parser_classes = (
        parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser)

    def post(self, request, format=None):
        if request.data.get('image'):
            imageserializer = PostImageSerializer(data=request.data)
            if imageserializer.is_valid():
                postimage = imageserializer.save(
                    uploader=request.user
                )
                return Response({'image_url': postimage.image.url})
        return Response()
