# Generated by Django 2.1.5 on 2021-12-29 22:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ekatagp', '0001_initial'),
        ('donation', '0008_auto_20190131_2243'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donation',
            name='coinbase_charge',
        ),
        migrations.AddField(
            model_name='donation',
            name='ekatagp_form',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ekatagp.PaymentForm'),
        ),
    ]
