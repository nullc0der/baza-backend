import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation)

from versatileimagefield.fields import VersatileImageField

from notifications.models import Notification


class BasicGroup(models.Model):
    GROUP_TYPES = (
        ('1', _('Art')),
        ('2', _('Activist')),
        ('3', _('Political')),
        ('4', _('News')),
        ('5', _('Business')),
        ('6', _('Government')),
        ('7', _('Blog')),
        ('8', _('Nonprofit Organization')),
        ('9', _('Other')),
    )
    JOIN_STATUS = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('request', 'Request'),
        ('invite', 'Invite')
    )
    name = models.CharField(verbose_name=_('Name'), max_length=40)
    about = models.CharField(
        verbose_name=_('About'), default='', max_length=300)
    group_type = models.CharField(
        verbose_name=_('Group Type'), max_length=30, choices=GROUP_TYPES)
    group_type_other = models.CharField(
        verbose_name=_('Please Specify'),
        max_length=30,
        null=True,
        blank=True
    )
    join_status = models.CharField(
        default='open', choices=JOIN_STATUS, max_length=30
    )
    header_image = VersatileImageField(
        upload_to='group_headers/',
        null=True,
        blank=True
    )
    logo = VersatileImageField(
        upload_to='group_logos/',
        null=True,
        blank=True
    )
    group_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    super_admins = models.ManyToManyField(User, related_name='basicgroups')
    admins = models.ManyToManyField(User, related_name='administerd_groups')
    staffs = models.ManyToManyField(User, related_name='staff_in_groups')
    moderators = models.ManyToManyField(User, related_name='moderating_groups')
    members = models.ManyToManyField(User, related_name='joined_group')
    subscribers = models.ManyToManyField(User, related_name='subscribed_group')
    banned_members = models.ManyToManyField(User, related_name='banned_group')
    blocked_members = models.ManyToManyField(
        User, related_name='blocked_group')
    default_roles = models.TextField(
        default='superadmin;admin;moderator;member;subscriber',
        editable=False
    )  # seperated by ';' from higher permission level to lower
    created_on = models.DateTimeField(auto_now_add=True)
    auto_approve_post = models.BooleanField(default=True, blank=True)
    auto_approve_comment = models.BooleanField(default=True, blank=True)
    is_beta_test_group = models.BooleanField(default=False)
    is_site_owner_group = models.BooleanField(default=False)
    flagged_for_deletion = models.BooleanField(default=False)
    flagged_for_deletion_on = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.flagged_for_deletion:
            self.flagged_for_deletion_on = None
        super(BasicGroup, self).save(*args, **kwargs)


class GroupNotification(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    basic_group = models.ForeignKey(
        BasicGroup, related_name='notifications', on_delete=models.CASCADE)
    notification = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)
    is_important = models.BooleanField(default=False)


class GroupInvite(models.Model):
    basic_group = models.ForeignKey(
        BasicGroup, related_name='invites', on_delete=models.CASCADE)
    sender = models.ForeignKey(
        User, related_name='sent_invites', on_delete=models.CASCADE)
    reciever = models.ForeignKey(
        User, related_name='received_invites', on_delete=models.CASCADE)
    sent_on = models.DateTimeField(auto_now_add=True)
    mainfeed = GenericRelation(Notification)  # Main Notification feed


class InviteAccept(models.Model):
    basic_group = models.ForeignKey(
        BasicGroup, related_name='accepted_invite', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name='invited_accept', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)


class JoinRequest(models.Model):
    basic_group = models.ForeignKey(
        BasicGroup, on_delete=models.CASCADE, related_name='joinrequest')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)


class GroupMemberNotification(models.Model):
    read = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, related_name='group_member_notifications',
        on_delete=models.CASCADE)
    basic_group = models.ForeignKey(BasicGroup, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    mainfeed = GenericRelation(Notification)  # Main Notification feed
