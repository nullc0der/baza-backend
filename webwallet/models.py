from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

# Create your models here.


class UserWebWallet(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='wallets')
    name = models.CharField(max_length=20)
    address = models.TextField(max_length=40)
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_default:
            qs = type(self).objects.filter(
                Q(is_default=True) & Q(user=self.user))
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            qs.update(is_default=False)

        super(UserWebWallet, self).save(*args, **kwargs)

    def __str__(self):
        return "{}'s {}".format(
            self.user.username, self.name)
