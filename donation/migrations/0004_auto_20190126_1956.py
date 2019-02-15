# Generated by Django 2.1.4 on 2019-01-26 19:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coinbasepay', '0008_chargepayment_is_rewarded'),
        ('donation', '0003_auto_20180804_1741'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donation',
            name='stripe_payment',
        ),
        migrations.AddField(
            model_name='donation',
            name='coinbase_charge',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='coinbasepay.Charge'),
        ),
        migrations.AddField(
            model_name='donation',
            name='is_pending',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='donation',
            name='logged_ip',
            field=models.GenericIPAddressField(null=True),
        ),
    ]