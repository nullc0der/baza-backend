from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer

from group.models import BasicGroup


class BasicGroupSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    subscribers = serializers.SerializerMethodField()
    header_image_url = VersatileImageFieldSerializer(
        sizes=[
            ('full_size', 'url')
        ],
        allow_null=True
    )
    logo_url = VersatileImageFieldSerializer(
        sizes=[
            ('full_size', 'url')
        ],
        allow_null=True
    )
    group_type = serializers.SerializerMethodField()
    user_permission_set = serializers.SerializerMethodField()

    def get_members(self, obj):
        return [
            member.profile.username or member.username
            for member in obj.members.all()]

    def get_subscribers(self, obj):
        return [
            subscriber.profile.username or subscriber.username
            for subscriber in obj.subscribers.all()]

    def get_group_type(self, obj):
        return obj.group_type_other\
            if obj.get_group_type_display() == 'Other'\
            else obj.get_group_type_display()

    def get_user_permission_set(self, obj):
        member = self.context['user']
        subscribed_groups = []
        if member in obj.subscribers.all():
            subscribed_groups.append(101)
        if member in obj.members.all():
            subscribed_groups.append(102)
        if member in obj.super_admins.all():
            subscribed_groups.append(103)
        if member in obj.admins.all():
            subscribed_groups.append(104)
        if member in obj.moderators.all():
            subscribed_groups.append(105)
        if member in obj.staffs.all():
            subscribed_groups.append(106)
        if member in obj.banned_members.all():
            subscribed_groups.append(107)
        if member in obj.blocked_members.all():
            subscribed_groups.append(108)
        return subscribed_groups

    def create(self, validated_data):
        owner = self.context['user']
        basicgroup = BasicGroup.objects.create(**validated_data)
        basicgroup.super_admins.add(owner)
        basicgroup.admins.add(owner)
        basicgroup.members.add(owner)
        basicgroup.subscribers.add(owner)
        return basicgroup

    class Meta:
        model = BasicGroup
        fields = (
            'id', 'name', 'short_about', 'long_about',
            'group_type', 'group_type_other', 'header_image_url', 'logo_url',
            'members', 'subscribers', 'auto_approve_post',
            'auto_approve_comment', 'join_status', 'flagged_for_deletion',
            'flagged_for_deletion_on', 'user_permission_set'
        )
