# Generated by Django 2.1.4 on 2019-01-31 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donation', '0006_auto_20190131_2158'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='is_anonymous',
            field=models.BooleanField(default=False),
        ),
    ]