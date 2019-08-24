from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "This command deletes the signup object for specified username"

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username=options['username'])
            user.bazasignup.delete()
            self.stdout.write(self.style.SUCCESS(
                "Signup deleted successfully"))
        except User.DoesNotExist:
            raise CommandError("The specified user does not exist")
