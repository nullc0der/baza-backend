# Generated by Django 2.1.3 on 2018-11-22 19:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('taigaissuecreator', '0003_auto_20180921_2119'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaigaIssueType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('color', models.CharField(max_length=10)),
                ('issue_type_id', models.CharField(max_length=40)),
                ('issue_type_order', models.CharField(max_length=10)),
                ('issue_type_project_id', models.CharField(max_length=40)),
            ],
        ),
        migrations.AddField(
            model_name='taigaissue',
            name='taiga_issue_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='taigaissuecreator.TaigaIssueType'),
        ),
    ]
