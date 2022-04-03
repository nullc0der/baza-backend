import csv
from typing import Any, Optional

from django.template import loader
from django.core.management.base import BaseCommand, CommandParser
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from django.conf import settings

from authclient.utils import AuthHelperClient

URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


class Command(BaseCommand):
    help = "This command will send balance"
    " check reminder eblast to active users"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--send-test', action='store_true',
                            help="Send email to admin for test")

    def send_email(self, email_id: str, username: str) -> None:
        template = loader.get_template(
            'eblast/check_balance_reminder.html')
        msg = EmailMultiAlternatives(
            'Check your balance on baza.foundation',
            'Check html message',
            'system-noreply@baza.foundation',
            [email_id]
        )
        msg.attach_alternative(
            template.render({
                'username': username
            }),
            "text/html"
        )
        msg.send()

    def get_username_and_emails(self, send_test: bool = False) -> None:
        if send_test:
            return [
                {
                    'email_id': 'prasantakakati@ekata.io',
                    'username': 'prasanta'
                },
                {
                    'email_id': 'andrew@ekata.io',
                    'username': 'puffmushroom'
                }
            ]
        users = User.objects.filter(
            last_login__lte=now() - timedelta(days=30)).exclude(
                username='paulhyatt')
        username_and_emails = []
        authhelperclient = AuthHelperClient(
            URL_PROTOCOL +
            settings.CENTRAL_AUTH_INTROSPECT_URL +
            '/authhelper/useremails/'
        )
        for user in users:
            if hasattr(user, 'bazasignup'):
                bazasignup = user.bazasignup
                if bazasignup.status == 'approved' and\
                    bazasignup.on_distribution and bool(
                        bazasignup.verified_date) and hasattr(
                            user, 'proxcaccount') and bool(
                        user.proxcaccount.balance):
                    status_code, data = authhelperclient.get_user_emails(
                        user.username)
                    if status_code == 200:
                        for i in data:
                            if i['primary'] and\
                                    i['email'] != 'carol.chalke546@yahoo.com':
                                username_and_emails.append({
                                    'email_id': i['email'],
                                    'username': user.username
                                })
        return username_and_emails

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        self.stdout.write(self.style.SUCCESS("Getting username and emails"))
        sent_to_emailids = []
        username_and_emails = self.get_username_and_emails(
            send_test=options["send_test"])
        for username_and_email in username_and_emails:
            self.stdout.write(self.style.SUCCESS(
                f"Sending email to {username_and_email['email_id']}"))
            self.send_email(
                email_id=username_and_email['email_id'],
                username=username_and_email['username'])
            sent_to_emailids.append(username_and_email)
        with open('balance_reminder.csv', 'w') as csvfile:
            csvwriter = csv.writer(
                csvfile, delimiter=',', quotechar='|',
                quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(['email_id', 'username'])
            for sent_to_emailid in sent_to_emailids:
                csvwriter.writerow(
                    [sent_to_emailid['email_id'], sent_to_emailid['username']])
        self.stdout.write(self.style.SUCCESS('Done'))
