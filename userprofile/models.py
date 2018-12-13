from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from pyotp import random_base32, totp


def user_directory(instance, filename):
    if isinstance(instance, UserPhoto):
        directory = 'userphotos'
    if isinstance(instance, UserDocument):
        directory = 'userdocuments'
    return '{0}/user_{1}/{2}'.format(
        directory, instance.profile.user.id, filename)


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=20, default='', blank=True)
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, default='male'
    )
    about_me = models.TextField(null=True, blank=True)
    website = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=15, default='')
    default_avatar_color = models.CharField(
        max_length=8, default='#7b1fa2')

    def __str__(self):
        return self.user.username


class UserPhoto(models.Model):
    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to=user_directory)


class UserProfilePhoto(models.Model):
    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE,
        related_name='profilephotos', null=True)
    userphoto = models.ForeignKey(
        UserPhoto, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)


class UserDocument(models.Model):
    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to=user_directory)


class UserPhone(models.Model):
    PHONE_NUMBER_CHOICES = (
        ('office', 'Office'),
        ('home', 'Home'),
        ('mobile', 'Mobile'),
        ('emergency', 'Emergency')
    )
    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='phones'
    )
    phone_number = models.CharField(max_length=15, default='')
    phone_number_type = models.CharField(
        max_length=10, default='office', choices=PHONE_NUMBER_CHOICES)
    primary = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.primary:
            qs = type(self).objects.filter(primary=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            qs.update(primary=False)

        super(UserPhone, self).save(*args, **kwargs)


class UserPhoneValidation(models.Model):
    userphone = models.OneToOneField(UserPhone, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6)
    created_on = models.DateTimeField(auto_now_add=True)


class UserTwoFactor(models.Model):
    TWO_FACTOR_TYPE_CHOICES = (
        ('totp', 'Totp'),
        ('hotp', 'Hotp'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('voice', 'Voice')
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='two_factor')
    two_factor_type = models.CharField(
        default='totp', max_length=10, choices=TWO_FACTOR_TYPE_CHOICES)
    secret_key = models.CharField(max_length=50, default=random_base32)
    enabled = models.BooleanField(default=False)

    def get_totp_provisioning_uri(self):
        return totp.TOTP(self.secret_key).provisioning_uri(
            name=self.user.profile.username or self.user.username,
            issuer_name=settings.HOST_URL
        )

    def verify_totp(self, otp):
        return totp.TOTP(self.secret_key).verify(otp)


class UserTwoFactorRecovery(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='two_factor_recovery')
    code = models.CharField(max_length=6)
    valid = models.BooleanField(default=True)


class UserTasks(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    added_and_validated_email = models.BooleanField(default=False)
    added_and_validated_phone = models.BooleanField(default=False)
    added_location = models.BooleanField(default=False)
    added_two_factor_authentication = models.BooleanField(default=False)
    linked_one_social_account = models.BooleanField(default=False)
    completed_distribution_signup = models.BooleanField(default=False)


class UserTrustPercentage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    percentage = models.PositiveIntegerField(default=0)
