from django.core.management.base import BaseCommand

from bazaback.imagesanitizer import sanitize_image
from userprofile.models import UserPhoto, UserDocument
from bazasignup.models import BazaSignup


class Command(BaseCommand):
    help = "This command will sanitize uploaded userphoto," + \
        "userdocument and bazasignup images"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            "Sanitizing UserPhotos..."))
        for userphoto in UserPhoto.objects.all():
            if userphoto.photo:
                self.stdout.write(
                    self.style.SUCCESS("Sanitizing UserPhoto %s" % userphoto.id))
                sanitized_image = sanitize_image(userphoto.photo)
                if sanitized_image:
                    userphoto.photo = sanitized_image
                    userphoto.save()
        self.stdout.write(self.style.SUCCESS("UserPhotos sanitized"))
        self.stdout.write(self.style.SUCCESS(
            "Sanitizing UserDocument..."))
        for userdocument in UserDocument.objects.all():
            if userdocument.document:
                self.stdout.write(
                    self.style.SUCCESS(
                        "Sanitizing UserDocument %s" % userdocument.id))
                sanitized_image = sanitize_image(userdocument.document)
                if sanitized_image:
                    userdocument.document = sanitized_image
                    userdocument.save()
        self.stdout.write(self.style.SUCCESS("UserDocuments sanitized"))
        self.stdout.write(self.style.SUCCESS(
            "Sanitizing BazaSignup images.."))
        for signup in BazaSignup.objects.all():
            if signup.photo:
                self.stdout.write(
                    self.style.SUCCESS(
                        "Sanitizing BazaSignup Image %s" % signup.id))
                sanitized_image = sanitize_image(signup.photo)
                if sanitized_image:
                    signup.photo = sanitized_image
                    signup.save()
        self.stdout.write(self.style.SUCCESS("BazaSignup images sanitized"))
