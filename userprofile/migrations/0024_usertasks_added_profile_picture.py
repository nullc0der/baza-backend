# Generated by Django 2.1.4 on 2019-03-15 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0023_userphone_phone_number_country_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertasks',
            name='added_profile_picture',
            field=models.BooleanField(default=False),
        ),
    ]