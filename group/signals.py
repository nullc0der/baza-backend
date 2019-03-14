from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_save
from django.contrib.auth.models import User
from django.conf import settings

from group.models import BasicGroup
from authclient.utils import AuthHelperClient


URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


@receiver(m2m_changed, sender=BasicGroup.members.through)
def add_member_access_to_beta(instance, **kwargs):
    pk_set = kwargs.pop('pk_set')
    action = kwargs.pop('action')
    model = kwargs.pop('model')
    authhelperclient = AuthHelperClient(
        URL_PROTOCOL +
        settings.CENTRAL_AUTH_INTROSPECT_URL +
        '/authhelper/updateuserscope/'
    )
    if instance.is_beta_test_group and action == 'post_add':
        for pk in pk_set:
            user = model.objects.get(id=pk)
            authhelperclient.update_user_special_scope(
                'add', 'baza-beta', user.username)


@receiver(m2m_changed, sender=BasicGroup.members.through)
def remove_member_access_to_beta(instance, **kwargs):
    pk_set = kwargs.pop('pk_set')
    action = kwargs.pop('action')
    model = kwargs.pop('model')
    authhelperclient = AuthHelperClient(
        URL_PROTOCOL +
        settings.CENTRAL_AUTH_INTROSPECT_URL +
        '/authhelper/updateuserscope/'
    )
    if instance.is_beta_test_group and action == 'post_remove':
        for pk in pk_set:
            user = model.objects.get(id=pk)
            authhelperclient.update_user_special_scope(
                'remove', 'baza-beta', user.username)


@receiver(post_save, sender=User)
def add_user_to_site_owner_group(sender, **kwargs):
    instance = kwargs['instance']
    if kwargs['created']:
        try:
            basicgroup = BasicGroup.objects.get(
                is_site_owner_group=True)
            basicgroup.members.add(instance)
        except BasicGroup.DoesNotExist:
            pass
