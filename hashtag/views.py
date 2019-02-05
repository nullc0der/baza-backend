import os
import tempfile
from itertools import zip_longest

import tweepy

from django.conf import settings
from django.shortcuts import render

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import (
    FormParser, MultiPartParser, JSONParser)

from oauth2_provider.contrib.rest_framework import TokenHasScope

from authclient.utils import AuthHelperClient

from hashtag.utils import get_hashtag_uid, get_final_file
from hashtag.models import HashtagImage


URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


class DownloadSocialPhotoView(views.APIView):
    """
    This API is used to download an users current social profile photo
    """

    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/usersocialphoto/'
        )
        res_status, data = authhelperclient.get_user_social_profile_photo(
            request.META['HTTP_AUTHORIZATION'].split(' ')[1],
            request.query_params.get('provider', 'facebook')
        )
        if res_status == 200:
            # TODO: download and save the photo from response url
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

    def save_hashtag_image(self, request):
        hashtag_image = HashtagImage(
            user=request.user,
            image=get_final_file(request.data['photo']),
            uid=get_hashtag_uid()
        )
        hashtag_image.save()
        return Response({
            'url': "{0}{1}/hashtagimage/{2}/".format(
                URL_PROTOCOL,
                settings.HOST_URL,
                hashtag_image.uid
            )
        })

    def upload_photo_to_twitter(self, request):
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
            tmp_file = tempfile.NamedTemporaryFile(
                prefix='twitter',
                suffix='.png',
                delete=False
            )
            tmp_file.writelines(request.data['photo'])
            tmp_file.close()
            auth = tweepy.OAuthHandler(
                data['consumer_key'], data['consumer_secret'])
            auth.set_access_token(
                data["oauth_token"], data["oauth_token_secret"])
            api = tweepy.API(auth)
            api.update_profile_image(tmp_file.name)
            os.remove(tmp_file.name)
            return Response({'url': None})
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        if request.data['provider'] == 'facebook':
            return self.save_hashtag_image(request)
        if request.data['provider'] == 'twitter':
            return self.upload_photo_to_twitter(request)


def facebook_share_view(request, uid):
    hashtagimage = HashtagImage.objects.get(uid=uid)
    otherimages = HashtagImage.objects.all().exclude(uid=uid).order_by('-id')
    otherimages = otherimages if otherimages.count(
    ) >= 12 else otherimages[0:12]
    otherimages_chunk = list(zip_longest(*[iter(otherimages)]*4))
    return render(
        request,
        'hashtag/fbshare.html',
        {
            'mainimage': hashtagimage,
            'otherimages_chunk': otherimages_chunk,
            'fb_app_id': settings.FACEBOOK_APP_ID,
            'host': '{0}{1}'.format(
                URL_PROTOCOL,
                settings.HOST_URL
            )
        }
    )
