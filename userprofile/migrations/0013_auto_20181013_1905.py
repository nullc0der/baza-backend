# Generated by Django 2.1.2 on 2018-10-13 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0012_auto_20181008_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='website',
            field=models.TextField(blank=True, null=True),
        ),
    ]
