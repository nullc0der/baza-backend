# Generated by Django 2.1.2 on 2018-11-04 21:56

from django.db import migrations
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basicgroup',
            name='header_image',
            field=versatileimagefield.fields.VersatileImageField(blank=True, null=True, upload_to='group_headers/'),
        ),
        migrations.AlterField(
            model_name='basicgroup',
            name='logo',
            field=versatileimagefield.fields.VersatileImageField(blank=True, null=True, upload_to='group_logos/'),
        ),
    ]
