from django.db import models
from django.contrib.auth.models import User

from simple_history.models import HistoricalRecords


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
    referred_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='referred_signups')
    is_donor = models.BooleanField(default=False)
    signup_date = models.DateTimeField(auto_now_add=True)
    verified_date = models.DateTimeField(null=True)
    wallet_address = models.CharField(max_length=40, default='')
    on_distribution = models.BooleanField(default=False)
    # Comma separated string if multiple
    completed_steps = models.CharField(max_length=10)
    # Comma separated string if multiple
    invalidated_steps = models.CharField(max_length=10)
    # Comma separated string if multiple
    invalidated_fields = models.CharField(max_length=300, default='')
    logged_ip_address = models.GenericIPAddressField(null=True)
    email_skipped = models.BooleanField(default=False)
    phone_skipped = models.BooleanField(default=False)
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='bazasignupchanges')
    history = HistoricalRecords()

    def get_completed_steps(self):
        return list(filter(None, self.completed_steps.split(',')))

    def get_invalidated_steps(self):
        return list(filter(None, self.invalidated_steps.split(',')))

    def get_invalidated_fields(self):
        return list(filter(None, self.invalidated_fields.split(',')))

    @property
    def _history_user(self):
        return self.changed_by


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
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='bazasignupaddresschanges')
    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.changed_by


class BazaSignupAdditionalInfo(models.Model):
    signup = models.OneToOneField(BazaSignup, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True)
    invalidation_comment = models.TextField(default='')
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='bazasignupaddinfochanges')
    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.changed_by


class BazaSignupAutoApprovalFailReason(models.Model):
    REASON_TYPE = (
        ('no_email', 'no_email'),
        ('no_phone', 'no_phone'),
        ('non_unique_email', 'non_unique_email'),
        ('non_unique_phone', 'non_unique_phone'),
        ('no_twilio_data', 'no_twilio_data'),
        ('no_geoip_data', 'no_geoip_data'),
        ('twilio_vs_userinput_address_range_exceed',
         'twilio_vs_userinput_address_range_exceed'),
        ('geoip_vs_userinput_address_range_exceed',
         'geoip_vs_userinput_address_range_exceed'),
        ('no_distance_fetched_twilio_vs_userinput',
         'no_distance_fetched_twilio_vs_userinput'),
        ('no_distance_fetched_geoip_vs_userinput',
         'no_distance_fetched_geoip_vs_userinput')
    )
    signup = models.ForeignKey(BazaSignup, on_delete=models.CASCADE)
    reason_type = models.CharField(
        max_length=100, choices=REASON_TYPE, default='')
    reason = models.TextField()
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='bazasignupfailreasonchanges')
    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.changed_by


class BazaSignupReferralCode(models.Model):
    signup = models.OneToOneField(BazaSignup, on_delete=models.CASCADE)
    code = models.CharField(max_length=12)


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


class BazaSignupComment(models.Model):
    signup = models.ForeignKey(
        BazaSignup, on_delete=models.CASCADE, related_name='comments')
    title = models.CharField(max_length=200)
    content = models.TextField()
    commented_on = models.DateTimeField(auto_now_add=True)
    commented_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bazasignupcomments')
