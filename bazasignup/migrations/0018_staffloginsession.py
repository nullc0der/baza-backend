# Generated by Django 2.1.5 on 2019-08-27 17:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bazasignup', '0017_auto_20190826_2057'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffLoginSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logged_in_at', models.DateTimeField(auto_now_add=True)),
                ('logged_out_at', models.DateTimeField()),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staffloginsessions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
