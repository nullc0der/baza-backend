# Generated by Django 2.1.4 on 2019-02-10 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0020_usertrustpercentage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ('quality_person', 'Quality Person')], default='quality_person', max_length=10),
        ),
    ]