# Generated by Django 2.1.1 on 2018-09-21 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taigaissuecreator', '0002_taigaissueattachment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taigaissueattachment',
            name='attachment',
            field=models.ImageField(upload_to='taiga_issue_images'),
        ),
    ]
