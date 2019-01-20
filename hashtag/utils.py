from django.utils.crypto import get_random_string

from hashtag.models import HashtagImage


def get_hashtag_uid():
    uid = get_random_string()
    is_not_unique = HashtagImage.objects.filter(uid=uid).count() > 0
    while is_not_unique:
        get_hashtag_uid()
    return uid
