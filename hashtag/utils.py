from mimetypes import MimeTypes

from django.utils.crypto import get_random_string

from hashtag.models import HashtagImage


def get_hashtag_uid():
    uid = get_random_string()
    is_not_unique = HashtagImage.objects.filter(uid=uid).count() > 0
    while is_not_unique:
        get_hashtag_uid()
    return uid


def get_final_file(photo):
    photo_name_splited = photo.name.split('.')
    if not len(photo_name_splited) > 1:
        extension = MimeTypes().guess_extension(photo.content_type)
        photo.name = photo_name_splited[0] + extension
    return photo
