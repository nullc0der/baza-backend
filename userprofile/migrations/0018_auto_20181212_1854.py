# Generated by Django 2.1.3 on 2018-12-12 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0017_userphonevalidation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userphonevalidation',
            name='verification_code',
            field=models.CharField(max_length=6),
        ),
    ]
