# Generated by Django 2.1.1 on 2018-09-24 20:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0005_auto_20180924_2027'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofilephoto',
            name='profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profilephotos', to='userprofile.UserProfile'),
        ),
        migrations.AlterField(
            model_name='userprofilephoto',
            name='userphoto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userprofile.UserPhoto'),
        ),
    ]
