from django.db import models
from django.contrib.auth.models import User

from versatileimagefield.fields import VersatileImageField

from group.models import BasicGroup


class GroupNews(models.Model):
    editor = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL)
    basic_group = models.ForeignKey(
        BasicGroup, related_name='news', on_delete=models.CASCADE)
    title = models.TextField(null=True)
    news = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    impressioncount = models.PositiveIntegerField(default=0)


class NewsImage(models.Model):
    uploader = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL)
    image = VersatileImageField(upload_to='group_news_images')
