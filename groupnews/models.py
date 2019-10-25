import markdown
import bleach
from bs4 import BeautifulSoup

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from versatileimagefield.fields import VersatileImageField

from group.models import BasicGroup


class GroupNews(models.Model):
    editor = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL)
    basic_group = models.ForeignKey(
        BasicGroup, related_name='news', on_delete=models.CASCADE)
    title = models.TextField(null=True)
    news = models.TextField()
    converted_news = models.TextField(default='')
    plaintext_news = models.TextField(default='')
    created_on = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    impressioncount = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        html = markdown.markdown(self.news)
        self.converted_news = bleach.clean(
            html,
            settings.BLEACH_VALID_TAGS,
            settings.BLEACH_VALID_ATTRS,
            settings.BLEACH_VALID_STYLES
        )
        self.plaintext_news = ''.join(BeautifulSoup(html).findAll(text=True))
        super(GroupNews, self).save(*args, **kwargs)


class NewsImage(models.Model):
    uploader = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL)
    image = VersatileImageField(upload_to='group_news_images')
