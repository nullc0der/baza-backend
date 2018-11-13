from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from group.models import (
    BasicGroup, GroupNotification, JoinRequest)
from publicusers.serializers import UserSerializer


class BasicGroupSerializer(serializers.ModelSerializer):
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
    members = serializers.SerializerMethodField()
    subscribers = serializers.SerializerMethodField()
    header_image_url = serializers.SerializerMethodField()
    join_request_sent = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    group_type = serializers.SerializerMethodField()
    user_permission_set = serializers.SerializerMethodField()
    logo = serializers.ImageField(write_only=True)
    header_image = serializers.ImageField(write_only=True)
    group_type_value = serializers.ChoiceField(
        choices=GROUP_TYPES, write_only=True, required=True,
        error_messages={"invalid_choice": "Please select a group type"}
    )

    def get_join_request_sent(self, obj):
        try:
            JoinRequest.objects.get(
                basic_group=obj,
                user=self.context['user']
            )
            return True
        except JoinRequest.DoesNotExist:
            return False

    def get_header_image_url(self, obj):
        datas = {}
        if obj.header_image:
            datas['full_size'] = obj.header_image.url
        return datas

    def get_logo_url(self, obj):
        datas = {}
        if obj.logo:
            datas['full_size'] = obj.logo.url,
            datas['thumbnail_92'] = obj.logo.thumbnail['92x92'].url
        return datas

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
        validated_data['group_type'] = validated_data.pop('group_type_value')
        basicgroup = BasicGroup.objects.create(**validated_data)
        basicgroup.super_admins.add(owner)
        basicgroup.admins.add(owner)
        basicgroup.members.add(owner)
        basicgroup.subscribers.add(owner)
        return basicgroup

    def update(self, instance, validated_data):
        if 'group_type_value' in validated_data:
            validated_data['group_type'] = validated_data.pop(
                'group_type_value')
        instance = super(BasicGroupSerializer, self).update(
            instance, validated_data)
        if instance.flagged_for_deletion:
            instance.flagged_for_deletion = False
            instance.flagged_for_deletion_on = None
            instance.save()
        return instance

    def validate(self, data):
        if 'group_type_value' in data:
            if data['group_type_value'] == '9' and\
                    not data['group_type_other']:
                raise serializers.ValidationError(
                    "You must specify the group type if you select other"
                )
            if data['group_type_value'] != '9' and data['group_type_other']:
                raise serializers.ValidationError(
                    "Other type must be blank if group type is not other"
                )
        return data

    class Meta:
        model = BasicGroup
        fields = (
            'id', 'name', 'short_about', 'long_about', 'join_request_sent',
            'group_type', 'group_type_value', 'group_type_other',
            'header_image_url', 'logo_url',
            'logo', 'header_image', 'members', 'subscribers',
            'auto_approve_post', 'auto_approve_comment', 'join_status',
            'flagged_for_deletion', 'flagged_for_deletion_on',
            'user_permission_set'
        )


class GroupMemberSerializer(serializers.Serializer):
    user = UserSerializer()
    user_permission_set = serializers.ListField()


class GroupNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupNotification
        fields = ('id', 'notification', 'created_on', 'is_important')


class GroupJoinRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    user = UserSerializer()
