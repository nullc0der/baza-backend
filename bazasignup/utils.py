import hashlib
from datetime import timedelta, datetime

from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from twilio.rest import Client

from authclient.utils import AuthHelperClient

from publicusers.views import get_username, get_avatar_color
from userprofile.views import get_profile_photo

from bazasignup.models import (
    PhoneVerification,
    EmailVerification,
    BazaSignup,
    BazaSignupReferralCode,
    BazaSignupEmail,
    BazaSignupPhone
)

URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


def send_email_verfication_code(email, signup_id):
    signup = BazaSignup.objects.get(id=signup_id)
    verification_code = get_random_string(length=6, allowed_chars='0123456789')
    email_template = loader.get_template('bazasignup/verification_code.html')
    msg = EmailMultiAlternatives(
        'Validate email for baza distribution signup',
        'Validate your email with code %s,'
        ' valid for 2 minute' % verification_code,
        'emailvalidation-noreply@baza.foundation',
        [email])
    msg.attach_alternative(email_template.render({
        'verification_code': verification_code
    }), "text/html")
    msg.send()
    email_verification, created = EmailVerification.objects.get_or_create(
        signup=signup
    )
    email_verification.email = email
    email_verification.verification_code = verification_code
    email_verification.save()
    return True


def send_email_verfication_code_again(signup_id):
    signup = BazaSignup.objects.get(id=signup_id)
    email_verification, created = EmailVerification.objects.get_or_create(
        signup=signup
    )
    if email_verification.created_on + timedelta(seconds=120) < now():
        email_verification.verification_code = get_random_string(
            length=6, allowed_chars='0123456789')
    email_verification.created_on = now()
    email_verification.save()
    verification_code = email_verification.verification_code
    email_template = loader.get_template('bazasignup/verification_code.html')
    msg = EmailMultiAlternatives(
        'Validate email for baza distribution signup',
        'Validate your email with code %s,'
        ' valid for 2 minute' % verification_code,
        'emailvalidation-noreply@baza.foundation',
        [email_verification.email])
    msg.attach_alternative(email_template.render({
        'verification_code': verification_code
    }), "text/html")
    msg.send()
    return True


def send_phone_verification_code(signup_id, phone_number):
    signup = BazaSignup.objects.get(id=signup_id)
    verification_code = get_random_string(length=6, allowed_chars='0123456789')
    message_body = \
        "Use code %s for baza signup\n valid for 2 minute" % verification_code
    client = Client(
        settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message_body,
        to=phone_number,
        from_=settings.TWILIO_PHONE_NO
    )
    phone_verification, created = PhoneVerification.objects.get_or_create(
        signup=signup
    )
    phone_verification.verification_code = verification_code
    phone_verification.phone_number = phone_number
    phone_verification.save()
    return message.status


def send_phone_verification_code_again(signup_id):
    signup = BazaSignup.objects.get(id=signup_id)
    phone_verification, created = PhoneVerification.objects.get_or_create(
        signup=signup
    )
    if phone_verification.created_on + timedelta(seconds=120) < now():
        phone_verification.verification_code = get_random_string(
            length=6, allowed_chars='0123456789')
    phone_verification.created_on = now()
    phone_verification.save()
    verification_code = phone_verification.verification_code
    message_body = \
        "Use code %s for baza signup\n valid for 2 minute" % verification_code
    client = Client(
        settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message_body,
        to=phone_verification.phone_number,
        from_=settings.TWILIO_PHONE_NO
    )
    return message.status


def get_unique_referral_code():
    """
    This function will return an unique referral code by creating md5sum of
    current unix timestamp, it will make final result uppercased and remove
    confusing character like 1, 0, I, O.

    NOTE: I am checking if the final code is already exist, please research
    if it needs to be checked or not
    """

    restricted_chars = ['1', '0', 'I', 'O']
    timestamp = str(datetime.utcnow().timestamp()).encode('utf-8')
    timestamp_md5 = hashlib.md5(timestamp).hexdigest()[:8].upper()
    if bool([i for i in timestamp_md5 if i in restricted_chars]):
        return get_unique_referral_code()
    if BazaSignupReferralCode.objects.filter(code=timestamp_md5).exists():
        return get_unique_referral_code()
    return 'BAZ-{}'.format(timestamp_md5)


# def get_unique_referral_code():
#     referral_code = get_random_string(
#         allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890',
#         length=6
#     )
#     ref_code_exist = BazaSignupReferralCode.objects.filter(
#         code=referral_code).exists()
#     if ref_code_exist:
#         return get_unique_referral_code()
#     return referral_code


def process_after_approval(signup_id):
    system_user = User.objects.get(username='system')
    signup = BazaSignup.objects.get(id=signup_id)
    referral_code = get_unique_referral_code()
    bazasignupreferralcode, created = \
        BazaSignupReferralCode.objects.get_or_create(
            signup=signup
        )
    if created:
        bazasignupreferralcode.code = referral_code
        bazasignupreferralcode.save()
    email_template = loader.get_template('bazasignup/approval_mail.html')
    msg = EmailMultiAlternatives(
        'You are approved for Baza Distribution',
        'Your referral code is %s' % bazasignupreferralcode.code,
        'distsignup-noreply@baza.foundation',
        [signup.email])
    msg.attach_alternative(email_template.render({
        'referral_code': bazasignupreferralcode.code,
        'referral_url':
            'https://baza.foundation/profile/'
            '#!baza-registration?referral-code=%s'
            % bazasignupreferralcode.code
    }), "text/html")
    msg.send()
    signup.verified_date = now()
    signup.changed_by = system_user
    signup.save()
    return True


def get_user_emails(user):
    try:
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/useremails/'
        )
        res_status, data = authhelperclient.get_user_emails(user.username)
        if res_status == 200:
            email_data = []
            for email in data:
                email_data.append({
                    'email_id': email.get('email', ''),
                    'primary': email.get('primary', False),
                    'verified': email.get('verified', False)
                })
            return email_data
    except ObjectDoesNotExist:
        pass
    return list()


def get_user_phones(user):
    data = []
    userphones = user.profile.phones.all()
    for userphone in userphones:
        data.append({
            'phone_number': userphone.get_full_phone_number(),
            'primary': userphone.primary,
            'verified': userphone.verified
        })
    return data


def get_signup_profile_data(signup):
    profile_datas = {
        'fullname': signup.user.get_full_name(),
        'username': get_username(signup.user),
        'user_image_url': get_profile_photo(signup.user),
        'user_avatar_color': get_avatar_color(signup.user),
        'birthdate': signup.bazasignupadditionalinfo.birth_date,
        'date_joined': signup.user.date_joined,
        'phones': get_user_phones(signup.user),
        'emails': get_user_emails(signup.user)
    }
    return profile_datas


def is_email_used_before(email):
    if email:
        bazasignupemail = BazaSignupEmail.objects.get(
            email=email
        )
        return bazasignupemail.signups.count() > 1
    return False


def is_phone_used_before(phone_number):
    if phone_number:
        bazasignupphone = BazaSignupPhone.objects.get(
            phone_number=phone_number
        )
        return bazasignupphone.signups.count() > 1
    return False


def get_address_data(address):
    data = {
        'address_type': address.address_type,
        'country': address.country,
        'city': address.city,
        'state': address.state,
        'house_number': address.house_number,
        'street_name': address.street,
        'zip_code': address.zip_code,
        'latitude': address.latitude,
        'longitude': address.longitude
    }
    return data


def is_address_fetched(signup, address_type):
    reason_type = 'no_geoip_data' if address_type == 'geoip_db' else\
        'no_twilio_data'
    fail_reasons = signup.bazasignupautoapprovalfailreason_set.filter(
        reason_type=reason_type)
    return not bool(fail_reasons)


def address_is_not_within_range(signup, address_type):
    reason_type = 'geoip_vs_userinput_address_range_exceed'\
        if address_type == 'geoip_db' else\
        'twilio_vs_userinput_address_range_exceed'
    fail_reasons = signup.bazasignupautoapprovalfailreason_set.filter(
        reason_type=reason_type)
    return bool(fail_reasons)


def get_signup_contact_data(signup):
    contact_data = {
        'email': signup.email,
        'email_used_before': is_email_used_before(signup.email),
        'phone_number': signup.phone_number,
        'phone_used_before': is_phone_used_before(signup.phone_number),
    }
    return contact_data


def get_signup_address_data(signup):
    address_data = {
        'addresses': [get_address_data(address)
                      for address in signup.addresses.all()],
        'twilio_address_fetched': is_address_fetched(signup, 'twilio_db'),
        'geoip_address_fetched': is_address_fetched(signup, 'geoip_db'),
        'geoip_address_is_not_within_range': address_is_not_within_range(
            signup, 'geoip_db'),
        'twilio_address_is_not_within_range': address_is_not_within_range(
            signup, 'twilio_db')
    }
    return address_data


def get_signup_additional_data(signup):
    additional_data = {
        'photo': signup.photo.url if signup.photo else '',
        'status': signup.status,
        'signup_date': signup.signup_date,
        'verified_date': signup.verified_date,
        'referral_code': signup.bazasignupreferralcode.code
        if hasattr(signup, 'bazasignupreferralcode') else '',
        'total_referrals': signup.user.referred_signups.count(),
        'is_donor': signup.is_donor,
        'referred_by': signup.referred_by.username
        if signup.referred_by else '',
        'wallet_address': signup.wallet_address,
        'on_distribution': signup.on_distribution
    }
    return additional_data


def get_signup_data(signup):
    signup_datas = {
        'id': signup.id,
        'contact_data': get_signup_contact_data(signup),
        'address_data': get_signup_address_data(signup),
        'additional_data': get_signup_additional_data(signup)
    }
    return signup_datas
