# Generated by Django 2.1.2 on 2018-10-08 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0011_auto_20181008_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertwofactorrecovery',
            name='valid',
            field=models.BooleanField(default=True),
        ),
    ]
