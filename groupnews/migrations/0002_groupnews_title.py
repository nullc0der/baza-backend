# Generated by Django 2.1.4 on 2019-03-21 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupnews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupnews',
            name='title',
            field=models.TextField(null=True),
        ),
    ]
