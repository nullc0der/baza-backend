# Generated by Django 2.1.4 on 2018-12-23 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinbasepay', '0005_auto_20181220_0015'),
    ]

    operations = [
        migrations.AddField(
            model_name='charge',
            name='charge_status_context',
            field=models.CharField(choices=[('OVERPAID', 'OVERPAID'), ('UNDERPAID', 'UNDERPAID'), ('MULTIPLE', 'MULTIPLE'), ('DELAYED', 'DELAYED'), ('MULTIPLE', 'MULTIPLE'), ('MANUAL', 'MANUAL'), ('OTHER', 'OTHER')], default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='charge',
            name='status',
            field=models.CharField(choices=[('NEW', 'NEW'), ('CONFIRMED', 'CONFIRMED'), ('FAILED', 'FAILED'), ('UNRESOLVED', 'UNRESOLVED'), ('RESOLVED', 'RESOLVED')], default='NEW', max_length=20),
        ),
    ]
