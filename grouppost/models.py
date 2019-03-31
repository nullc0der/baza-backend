import markdown
import bleach

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from versatileimagefield.fields import VersatileImageField

from group.models import BasicGroup


class GroupPost(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    basic_group = models.ForeignKey(
        BasicGroup, related_name='posts', on_delete=models.CASCADE)
    post = models.TextField()
    converted_post = models.TextField(default='')
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User, related_name='posts_approved', null=True, blank=True,
        on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        html = markdown.markdown(self.post)
        self.converted_post = bleach.clean(
            html,
            settings.BLEACH_VALID_TAGS,
            settings.BLEACH_VALID_ATTRS,
            settings.BLEACH_VALID_STYLES
        )
        super(GroupPost, self).save(*args, **kwargs)


class PostComment(models.Model):
    commentor = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(
        GroupPost, related_name='comments', on_delete=models.CASCADE)
    comment = models.TextField()
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User, related_name='approved_comments', null=True, blank=True,
        on_delete=models.SET_NULL)
    commented_on = models.DateTimeField(auto_now_add=True)


class PostImage(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    image = VersatileImageField(upload_to='group_post_images')
