from django.db import models
from django.contrib.auth.models import User


class BazaSignup(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('incomplete', 'Incomplete')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    photo = models.ImageField(upload_to='signup_images', null=True)
    email = models.EmailField(null=True)
    phone_number = models.CharField(max_length=15, default='')
    signup_date = models.DateTimeField(auto_now_add=True)
    verified_date = models.DateTimeField(null=True)
    referral_code = models.CharField(max_length=6, default='')
    wallet_address = models.CharField(max_length=40, default='')
    on_distribution = models.BooleanField(default=False)
    # Comma seprated string if multiple
    completed_steps = models.CharField(max_length=10)
    logged_ip_address = models.GenericIPAddressField(null=True)
    email_skipped = models.BooleanField(default=False)
    phone_skipped = models.BooleanField(default=False)

    def get_completed_steps(self):
        return self.completed_steps.split(',')


class BazaSignupAddress(models.Model):
    ADDRESS_TYPE = (
        ('user_input', 'user_input'),
        ('twilio_db', 'twilio_db'),
        ('geoip_db', 'geoip_db')
    )
    signup = models.ForeignKey(
        BazaSignup, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE)
    house_number = models.CharField(max_length=10, default='', blank=True)
    street = models.CharField(max_length=200, default='', blank=True)
    zip_code = models.CharField(max_length=10, default='', blank=True)
    city = models.CharField(max_length=100, default='', blank=True)
    state = models.CharField(max_length=100, default='', blank=True)
    country = models.CharField(max_length=100, default='', blank=True)
    latitude = models.CharField(max_length=100, default='', blank=True)
    longitude = models.CharField(max_length=100, default='', blank=True)


class BazaSignupAdditionalInfo(models.Model):
    signup = models.OneToOneField(BazaSignup, on_delete=models.CASCADE)
    birth_date = models.DateField()


class BazaSignupEmail(models.Model):
    email = models.EmailField()
    signups = models.ManyToManyField(BazaSignup, related_name='signup_emails')


class BazaSignupPhone(models.Model):
    phone_number = models.CharField(max_length=15)
    signups = models.ManyToManyField(BazaSignup, related_name='signup_phones')


class EmailVerification(models.Model):
    email = models.EmailField()
    signup = models.OneToOneField(BazaSignup, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6)
    created_on = models.DateTimeField(auto_now_add=True)


class PhoneVerification(models.Model):
    phone_number = models.CharField(max_length=15)
    signup = models.OneToOneField(BazaSignup, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6)
    created_on = models.DateTimeField(auto_now_add=True)
