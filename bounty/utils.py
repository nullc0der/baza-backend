from django.utils.timezone import now
from django.contrib.auth.models import User
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from proxcdb.models import ProxcTransaction
from coinpurchase.utils import get_user_access_token
from authclient.utils import AuthHelperClient

from bounty.models import BountyProgram, RewardedBounty
from bounty.bounties import BAZA_BAZ_BOUNTY_3

URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


def bounty_program_available(bounty_program, bounty_amount):
    if bounty_program.valid_till > now():
        if bounty_program.rewarded_amount + bounty_amount\
                < bounty_program.total_amount:
            return True
    return False


def make_reward_entries(bounty_task, user, bounty_program):
    RewardedBounty.objects.create(
        user=user,
        bounty_program=bounty_program,
        rewarded_for_task=bounty_task['name'],
        amount=bounty_task['amount']
    )
    bounty_program.rewarded_amount += bounty_task['amount']
    bounty_program.save()
    system_user = User.objects.get(username='system')
    transaction = ProxcTransaction(
        account=system_user.proxcaccount,
        to_account=user.proxcaccount,
        message='Reward for {}'.format(bounty_task['email_desc']),
        amount=bounty_task['amount'],
        should_substract_txfee=False
    )
    transaction.save()


def send_reward_email_to_user(bounty_task, user):
    access_token = get_user_access_token(user)
    authhelperclient = AuthHelperClient(
        URL_PROTOCOL +
        settings.CENTRAL_AUTH_INTROSPECT_URL +
        '/authhelper/useremails/'
    )
    if access_token:
        res_status, data = authhelperclient.get_user_emails(access_token)
        if res_status == 200:
            primary_emails = [
                email for email in data if email['primary']
                and email['verified']]
            if len(primary_emails):
                email_template = loader.get_template(
                    'bounty/reward_email.html')
                msg = EmailMultiAlternatives(
                    'Congratulations! You have received a reward',
                    'You received reward of {} for {}'.format(
                        bounty_task['amount'], bounty_task['email_desc']),
                    'bounty@baza.foundation',
                    [primary_emails[0]['email']])
                msg.attach_alternative(email_template.render({
                    'amount': bounty_task['amount'],
                    'email_desc': bounty_task['email_desc']
                }), "text/html")
                msg.send()


def send_reward(user_id, task_name, can_have_multiple=False, amount=0):
    bounty_program = BountyProgram.objects.get(name='BAZA_BAZ_BOUNTY_3')
    bounty_task = BAZA_BAZ_BOUNTY_3['tasks'][task_name]
    if amount != 0:
        bounty_task['amount'] = amount
    user = User.objects.get(id=user_id)
    if bounty_program_available(bounty_program, bounty_task['amount']):
        if can_have_multiple:
            make_reward_entries(bounty_task, user, bounty_program)
            send_reward_email_to_user(bounty_task, user)
            return "{} received {} bounty for {}".format(
                user.username, bounty_task['amount'], bounty_task['name'])
        else:
            try:
                RewardedBounty.objects.get(
                    bounty_program=bounty_program,
                    user=user,
                    rewarded_for_task=bounty_task['name'])
                return "Skipped {} bounty for {},".format(
                    bounty_task['name'], user.username) + \
                    " Reason: already_rewarded"
            except RewardedBounty.DoesNotExist:
                make_reward_entries(bounty_task, user, bounty_program)
                send_reward_email_to_user(bounty_task, user)
                return "{} received {} bounty for {}".format(
                    user.username, bounty_task['amount'], bounty_task['name'])
            except RewardedBounty.MultipleObjectReturned:
                return "Skipped {} bounty for {},".format(
                    bounty_task['name'], user.username) + \
                    " Reason: multiple_bounty_object"
    return "Skipped {} bounty for {}, Reason: bounty_program_invalid".format(
        bounty_task['name'], user.username)
