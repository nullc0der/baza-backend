import requests

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geoip2 import GeoIP2
from django.db.models import ObjectDoesNotExist

from twilio.rest import Client
from iso3166 import countries
from geopy.distance import great_circle

from bazasignup.models import (
    BazaSignup, BazaSignupAddress,
    BazaSignupEmail, BazaSignupPhone,
    BazaSignupAutoApprovalFailReason
)


class BazaSignupAutoApproval(object):
    def __init__(self, signup_id):
        self.signup = BazaSignup.objects.get(id=signup_id)
        self.system_user = User.objects.get(username='system')
        self.autoapproval_fail_reason = []

    def __get_twilio_data(self):
        if self.signup.phone_number:
            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            lookup = client.lookups.phone_numbers(
                self.signup.phone_number).fetch(
                    add_ons='whitepages_pro_caller_id')
            if lookup.add_ons['results'][
                    'whitepages_pro_caller_id']['status'] == 'successful':
                address_data = lookup.add_ons['results'][
                    'whitepages_pro_caller_id'][
                        'result']['current_addresses'][0]
                lat_long = address_data.get('lat_long', '')
                bazasignupaddress = BazaSignupAddress(
                    signup=self.signup,
                    address_type='twilio_db',
                    changed_by=self.system_user,
                    zip_code=address_data.get('postal_code', ''),
                    city=address_data.get('city', ''),
                    state=address_data.get('state_code', ''),
                    country=countries.get(address_data.get(
                        'country_code', '').lower()),
                    latitude=lat_long.get('latitude', ''),
                    longitude=lat_long.get('longitude', '')
                )
                bazasignupaddress.save()
                return True
        return False

    def __get_geoip_data(self):
        if self.signup.logged_ip_address:
            try:
                geoip2 = GeoIP2()
                address_data = geoip2.city(self.signup.logged_ip_address)
                bazasignupaddress = BazaSignupAddress(
                    signup=self.signup,
                    address_type='geoip_db',
                    changed_by=self.system_user,
                    city=address_data.get('city', ''),
                    country=address_data.get('country_name', ''),
                    zip_code=address_data.get('postal_code', ''),
                    latitude=address_data.get('latitude', ''),
                    longitude=address_data.get('longitude', '')
                )
                bazasignupaddress.save()
                return True
            except:
                pass
        return False

    def __get_coordinates(self, addresses):
        google_geolocation_api_key = settings.GOOGLE_GEOLOCATION_API_KEY
        for address in addresses:
            if address.zip_code:
                url = "https://maps.googleapis.com/" +\
                    "maps/api/geocode/json?address=%s&key=%s" % (
                        address.zip_code,
                        google_geolocation_api_key)
            else:
                if address.city and address.country:
                    url = "https://maps.googleapis.com/" +\
                        "maps/api/geocode/json?address=%s&key=%s" % (
                            address.city + ',' + address.country,
                            google_geolocation_api_key)
                else:
                    url = "https://maps.googleapis.com/" +\
                        "maps/api/geocode/json?address=%s&key=%s" % (
                            address.city,
                            google_geolocation_api_key)
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                if data['status'] == 'OK':
                    location = data['results'][0]['geometry']['location']
                    address.latitude = location['lat']
                    address.longitude = location['lng']
                    address.changed_by = self.system_user
                    address.save()

    def __collect_datas(self):
        address_with_no_coordinates = []
        twilio = self.__get_twilio_data()
        geoip = self.__get_geoip_data()
        for address in self.signup.addresses.all():
            if not address.latitude or not address.longitude:
                address_with_no_coordinates.append(address)
        self.__get_coordinates(address_with_no_coordinates)
        return {
            'twilio': twilio,
            'geoip': geoip
        }

    def __is_phone_unique(self):
        bazasignupphone = BazaSignupPhone.objects.get(
            phone_number=self.signup.phone_number
        )
        return bazasignupphone.signups.count() == 1

    def __is_email_unique(self):
        bazasignupemail = BazaSignupEmail.objects.get(
            email=self.signup.email
        )
        return bazasignupemail.signups.count() == 1

    # TEST: Decide which __get_distance method works better
    # def __get_distance(self, from_address, to_address):
    #     google_geolocation_api_key = settings.GOOGLE_GEOLOCATION_API_KEY
    #     origin = from_address.latitude + "," + from_address.longitude
    #     destination = to_address.latitude + "," + to_address.longitude
    #     url = "https://maps.googleapis.com/" +\
    #     "maps/api/distancematrix/json/?origins=%sdestinations=%s&key=%s" % (
    #         origin, destination, google_geolocation_api_key
    #     )
    #     res = requests.get(url)
    #     if res.status_code == 200:
    #         data = res.json()
    #         if data['rows'][0]['elements'][0]['status'] == 'OK':
    #             return data['rows'][0]['elements'][0]['distance']['value']
    #     return False

    def __get_distance(self, from_address, to_address):
        origin = (from_address.latitude, from_address.longitude)
        destination = (to_address.latitude, to_address.longitude)
        return great_circle(origin, destination).km

    def __compare_addresses(self):
        try:
            geoip_address = self.signup.addresses.get(
                address_type='geoip_db')
        except ObjectDoesNotExist:
            geoip_address = False
        try:
            twilio_address = self.signup.addresses.get(
                address_type='twilio_db')
        except ObjectDoesNotExist:
            twilio_address = False
        user_address = self.signup.addresses.get(address_type='user_input')
        geoip_vs_userinput = self.__get_distance(
            geoip_address, user_address) if geoip_address else False
        twilio_vs_userinput = self.__get_distance(
            twilio_address, user_address) if twilio_address else False
        return {
            'geoip_vs_userinput': geoip_vs_userinput,
            'twilio_vs_userinput': twilio_vs_userinput
        }

    def __process_auto_approval(self,
                                data_collection_status, address_distances):
        score = 0
        if self.signup.email:
            if self.__is_email_unique():
                score += 1
            else:
                score -= 1
                self.autoapproval_fail_reason.append({
                    'reason_type': 'non_unique_email',
                    'reason': 'Email address is not unique'
                })
        else:
            score -= 1
            self.autoapproval_fail_reason.append({
                'reason_type': 'no_email',
                'reason': 'No email address'
            })
        if self.signup.phone_number:
            if self.__is_phone_unique():
                score += 1
            else:
                score -= 1
                self.autoapproval_fail_reason.append({
                    'reason_type': 'non_unique_phone',
                    'reason': 'Phone number is not unique'
                })
        else:
            score -= 1
            self.autoapproval_fail_reason.append({
                'reason_type': 'no_phone',
                'reason': 'No phone number'
            })
        if data_collection_status['twilio']:
            score += 1
        else:
            score -= 1
            self.autoapproval_fail_reason.append({
                'reason_type': 'no_twilio_data',
                'reason': 'No twilio data could be fetched'
            })
        if data_collection_status['geoip']:
            score += 1
        else:
            score -= 1
            self.autoapproval_fail_reason.append({
                'reason_type': 'no_geoip_data',
                'reason': 'No geoip data could be fetched'
            })
        if address_distances['geoip_vs_userinput']:
            if address_distances['geoip_vs_userinput'] <\
                    settings.MAXIMUM_ALLOWED_DISTANCE_FOR_SIGNUP:
                score += 1
            else:
                score -= 1
                self.autoapproval_fail_reason.append({
                    'reason_type': 'geoip_vs_userinput_address_range_exceed',
                    'reason': 'Geoip and user inputed address difference'
                    ' exceeds maximum allowed distance'
                })
        else:
            score -= 1
            self.autoapproval_fail_reason.append({
                'reason_type': 'no_distance_fetched_geoip_vs_userinput',
                'reason': 'No distance could be fetched'
                ' between geoip and user inputed address'
            })
        if address_distances['twilio_vs_userinput']:
            if address_distances['twilio_vs_userinput'] <\
                    settings.MAXIMUM_ALLOWED_DISTANCE_FOR_SIGNUP:
                score += 1
            else:
                score -= 1
                self.autoapproval_fail_reason.append({
                    'reason_type': 'twilio_vs_userinput_address_range_exceed',
                    'reason': 'Twilio and user inputed address difference'
                    ' exceeds maximum allowed distance'
                })
        else:
            score -= 1
            self.autoapproval_fail_reason.append({
                'reason_type': 'no_distance_fetched_twilio_vs_userinput',
                'reason': 'No distance could be fetched'
                ' between twilio and user inputed address'
            })
        if score >= 3:
            self.signup.status == 'approved'
            self.signup.changed_by = self.system_user
            self.signup.save()
        else:
            for fail_reason in self.autoapproval_fail_reason:
                autoapprovalfailreason = BazaSignupAutoApprovalFailReason(
                    signup=self.signup,
                    reason_type=fail_reason['reason_type'],
                    reason=fail_reason['reason'],
                    changed_by=self.system_user
                )
                autoapprovalfailreason.save()
        return self.signup.status

    def start(self):
        data_collection_results = self.__collect_datas()
        address_distances = self.__compare_addresses()
        signup_status = self.__process_auto_approval(
            data_collection_results, address_distances)
        return signup_status
