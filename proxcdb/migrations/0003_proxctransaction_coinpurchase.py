# Generated by Django 2.1.4 on 2019-01-02 22:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coinpurchase', '0004_auto_20181227_2232'),
        ('proxcdb', '0002_auto_20181205_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='proxctransaction',
            name='coinpurchase',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='coinpurchase.CoinPurchase'),
        ),
    ]
