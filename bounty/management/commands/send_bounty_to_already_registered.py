from datetime import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.timezone import make_aware

from bounty.tasks import task_send_reward
from bounty.bounties import BAZA_BAZ_BOUNTY_1


class Command(BaseCommand):
    help = "This command will send reward to already registered user"

    def handle(self, *args, **options):
        timestamp = make_aware(datetime.strptime('2019-11-14', '%Y-%m-%d'))
        users = User.objects.filter(date_joined__gt=timestamp)
        for user in users:
            bounty_task_name = BAZA_BAZ_BOUNTY_1['tasks']['signed_up']['name']
            task_send_reward.delay(user.id, bounty_task_name)
            self.stdout.write(self.style.SUCCESS(
                'Sent signup reward to {}'.format(user.username)))
            if hasattr(user, 'bazasignup'):
                if user.bazasignup.status == 'approved':
                    signup = user.bazasignup
                    bounty_task_name = BAZA_BAZ_BOUNTY_1[
                        'tasks']['registered_and_approved_on_baz_distribution'
                                 ]['name']
                    task_send_reward.delay(
                        signup.user.id, bounty_task_name)
                    self.stdout.write(self.style.SUCCESS(
                        'Sent distribution registration reward to {}'.format(
                            user.username)
                    ))
                    if signup.referred_by:
                        bounty_task_name = BAZA_BAZ_BOUNTY_1[
                            'tasks']['referred_user_for_baz_distribution'][
                                'name']
                        task_send_reward.delay(
                            signup.referred_by.id, bounty_task_name,
                            can_have_multiple=True
                        )
                        self.stdout.write(self.style.SUCCESS(
                            'Sent distribution registration referral' +
                            ' reward to {}'.format(
                                signup.referred_by.username)
                        ))
