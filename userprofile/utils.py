from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.contrib.auth.models import User

from twilio.rest import Client

from authclient.utils import AuthHelperClient
from userprofile.models import (
    UserPhone, UserPhoneValidation, UserProfilePhoto, UserTasks,
    UserTrustPercentage, UserProfilePhoto)

URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


def send_two_factor_email(username, access_token, email_type):
    EMAIL_TEMPLATES = {
        0: 'userprofile/twofactorenabled.html',
        1: 'userprofile/twofactordisabled.html',
        2: 'userprofile/recoverycodedownloaded.html'
    }
    authhelperclient = AuthHelperClient(
        URL_PROTOCOL +
        settings.CENTRAL_AUTH_INTROSPECT_URL +
        '/authhelper/useremails/'
    )
    res_status, data = authhelperclient.get_user_emails(access_token)
    if res_status == 200:
        primary_emails = [
            email for email in data if email['primary'] and email['verified']]
        if len(primary_emails):
            email_template = loader.get_template(EMAIL_TEMPLATES[email_type])
            msg = EmailMultiAlternatives(
                subject='Account Alert',
                body='Two Factor Notification',
                from_email='system-noreply@baza.foundation',
                to=[primary_emails[0]['email']]
            )
            msg.attach_alternative(email_template.render({
                'username': username
            }), 'text/html')
            msg.send()


def user_has_verified_phone(user):
    userphones = UserPhone.objects.filter(profile=user.profile)
    for userphone in userphones:
        if userphone.verified:
            return True
    return False


def user_has_verified_email(access_token):
    authhelperclient = AuthHelperClient(
        URL_PROTOCOL +
        settings.CENTRAL_AUTH_INTROSPECT_URL +
        '/authhelper/useremails/'
    )
    res_status, data = authhelperclient.get_user_emails(access_token)
    if res_status == 200:
        primary_emails = [
            email for email in data if email['primary'] and email['verified']]
        return bool(len(primary_emails))
    return False


def user_has_two_factor(user):
    if hasattr(user, 'two_factor'):
        return user.two_factor.enabled
    return False


def user_has_social_account_linked(access_token):
    authhelperclient = AuthHelperClient(
        URL_PROTOCOL +
        settings.CENTRAL_AUTH_INTROSPECT_URL +
        '/authhelper/getsocialauths/'
    )
    res_status, data = authhelperclient.get_user_social_auths(access_token)
    if res_status == 200:
        return bool(len(data))
    return False


def user_has_completed_distribution_signup(user):
    if hasattr(user, 'bazasignup'):
        signup = user.bazasignup
        return len(signup.get_completed_steps()) == 4
    return False


def user_added_profile_picture(user):
    return bool(
        user.profile.profilephotos.filter(is_active=True))


def user_uploaded_an_official_document_id(user):
    return bool(user.profile.documents.count())


def user_added_location(user):
    if hasattr(user, 'bazasignup'):
        signup = user.bazasignup
        return bool(signup.addresses.filter(address_type='user_input'))
    return False


def compute_user_tasks(user_id, access_token):
    user = User.objects.get(id=user_id)
    usertasks, created = UserTasks.objects.get_or_create(user=user)
    usertasks.added_and_validated_email = user_has_verified_email(access_token)
    usertasks.added_and_validated_phone = user_has_verified_phone(user)
    usertasks.uploaded_an_official_document_id = user_uploaded_an_official_document_id(
        user)
    usertasks.added_location = user_added_location(user)
    usertasks.linked_one_social_account = user_has_social_account_linked(
        access_token)
    usertasks.added_profile_picture = user_added_profile_picture(user)
    usertasks.added_two_factor_authentication = user_has_two_factor(user)
    # usertasks.completed_distribution_signup =\
    #     user_has_completed_distribution_signup(user)
    usertasks.save()


def get_trust_percentile(usertrustpercentage):
    above_user = 0
    trustpercentages = UserTrustPercentage.objects.all()
    for trustpercentage in trustpercentages:
        if trustpercentage.percentage < usertrustpercentage.percentage:
            above_user += 1
    return round((above_user/trustpercentages.count()) * 100)


def get_user_tasks(usertasks):
    verified_email = usertasks.added_and_validated_email
    verified_phone = usertasks.added_and_validated_phone
    uploaded_an_official_document_id = usertasks.uploaded_an_official_document_id
    location = usertasks.added_location
    social_account_linked = usertasks.linked_one_social_account
    added_profile_picture = usertasks.added_profile_picture
    two_factor = usertasks.added_two_factor_authentication
    # completed_distribution_signup = usertasks.completed_distribution_signup
    tasks = [
        {
            'status': 'done' if verified_email else 'pending',
            'href': '#details',
            'id': 1,
            'description': 'Add an email id and verify'
        },
        {
            'status': 'done' if verified_phone else 'pending',
            'href': '#details',
            'id': 2,
            'description': 'Add a phone number and verify'
        },
        {
            'status': 'done' if uploaded_an_official_document_id else 'pending',
            'href': '#documents',
            'id': 3,
            'description': 'Upload an official document ID'
        },
        {
            'status': 'done' if location else 'pending',
            'href': '#profile',
            'id': 4,
            'description': 'Add your location'
        },
        {
            'status': 'done' if social_account_linked else 'pending',
            'href': '#details',
            'id': 5,
            'description': 'Link a social account'
        },
        {
            'status': 'done' if added_profile_picture else 'pending',
            'href': '#documents',
            'id': 6,
            'description': 'Add a profile picture'
        },
        {
            'status': 'done' if two_factor else 'pending',
            'href': '#security',
            'id': 7,
            'description': 'Enable two factor'
        },
        # {
        #     'status': 'done' if completed_distribution_signup else 'pending',
        #     'href': '#!baza-signup',
        #     'id': 6,
        #     'description': 'Complete distribution signup'
        # },
    ]
    trust_percentage = 0
    trust_percentage += 14.3 if uploaded_an_official_document_id else 0
    trust_percentage += 14.3 if verified_email else 0
    trust_percentage += 14.3 if verified_phone else 0
    trust_percentage += 14.3 if location else 0
    trust_percentage += 14.3 if two_factor else 0
    trust_percentage += 14.3 if social_account_linked else 0
    trust_percentage += 14.3 if added_profile_picture else 0
    if trust_percentage > 100:
        trust_percentage = 100
    usertrustpercentage, created = UserTrustPercentage.objects.get_or_create(
        user=usertasks.user)
    usertrustpercentage.percentage = trust_percentage
    usertrustpercentage.save()
    return {
        'tasks': tasks,
        'trust_percentage': trust_percentage,
        'trust_percentile': get_trust_percentile(usertrustpercentage)
    }


def send_phone_verification_code(phone_number):
    userphone = UserPhone.objects.get(phone_number=phone_number)
    verification_code = get_random_string(length=6, allowed_chars='0123456789')
    message_body = \
        "Use code %s to verify at\n" % verification_code +\
        "Baza Foundation profile, valid for 2 minute"
    client = Client(
        settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message_body,
        to=userphone.get_full_phone_number(),
        from_=settings.TWILIO_PHONE_NO
    )
    userphonevalidation, created = UserPhoneValidation.objects.get_or_create(
        userphone=userphone
    )
    userphonevalidation.verification_code = verification_code
    userphonevalidation.created_on = now()
    userphonevalidation.save()
    return message.status


def get_profile_photo(user):
    profile_photo = None
    try:
        profilephoto = user.profile.profilephotos.get(
            is_active=True)
        profile_photo = profilephoto.userphoto.photo.url
    except UserProfilePhoto.DoesNotExist:
        pass
    return profile_photo
