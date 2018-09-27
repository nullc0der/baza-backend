from django.db import models
from django.contrib.auth.models import User


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
    website = models.URLField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=15, default='')
    default_avatar_color = models.CharField(
        max_length=8, default='#7b1fa2')


class UserPhoto(models.Model):
    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='userphotos')


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
    document = models.FileField(upload_to='userdocuments')
