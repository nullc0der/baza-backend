# Generated by Django 2.1.4 on 2019-02-08 20:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coinpurchase', '0004_auto_20181227_2232'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coinpurchase',
            name='stripe_payment',
        ),
    ]
