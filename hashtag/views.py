import tweepy
from facepy import GraphAPI

from django.conf import settings

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import (
    FormParser, MultiPartParser, JSONParser)

from oauth2_provider.contrib.rest_framework import TokenHasScope

from authclient.utils import AuthHelperClient


URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


class DownloadSocialPhotoView(views.APIView):
    """
    This API is used to download an users current social profile photo
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/usersocialphoto/'
        )
        res_status, data = authhelperclient.get_user_social_profile_photo(
            request.META['HTTP_AUTHORIZATION'].split(' ')[1],
            request.data.get('provider', 'facebook')
        )
        if res_status == 200:
            # TODO: download and save the photo from response url
            return Response(data)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class GetSocialScopesView(views.APIView):
    """
    This API is used to get an users granted and denied scopes
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/usersocialscopes/'
        )
        res_status, data = authhelperclient.get_user_social_scopes(
            request.META['HTTP_AUTHORIZATION'].split(' ')[1],
            request.data.get('provider', 'facebook')
        )
        if res_status == 200:
            return Response(data)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UploadHashtagImageView(views.APIView):
    """
    This API will be used to upload hashtag image to users social account
    """

    parser_classes = (FormParser, MultiPartParser, JSONParser, )
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def upload_photo_to_facebook(self, photo, request):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/usersocialcredentials/'
        )
        res_status, data = authhelperclient.get_user_social_credentials(
            request.META['HTTP_AUTHORIZATION'].split(' ')[1],
            'facebook'
        )
        if res_status == 200:
            graph = GraphAPI(data['access_token'])
            graph.post(path='me/photos', source=photo)
            return Response()
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def upload_photo_to_twitter(self, photo, request):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/usersocialcredentials/'
        )
        res_status, data = authhelperclient.get_user_social_credentials(
            request.META['HTTP_AUTHORIZATION'].split(' ')[1],
            'twitter'
        )
        if res_status == 200:
            auth = tweepy.OAuthHandler(
                data['consumer_key'], data['consumer_secret'])
            auth.set_access_token(
                data["oauth_token"], data["oauth_token_secret"])
            api = tweepy.API(auth)
            api.update_profile_image(photo)
            return Response()
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        if request.data['provider'] == 'facebook':
            return self.upload_photo_to_facebook(request.data['photo'])
        if request.data['provider'] == 'twitter':
            return self.upload_photo_to_twitter(request.data['photo'])
