# Generated by Django 2.1.4 on 2018-12-19 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinbasepay', '0002_charge_charge_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charge',
            name='status',
            field=models.CharField(choices=[('NEW', 'NEW'), ('CONFIRMED', 'CONFIRMED'), ('FAILED', 'FAILED')], default='NEW', max_length=20),
        ),
    ]
