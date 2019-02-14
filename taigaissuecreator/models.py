from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class TaigaIssueType(models.Model):
    name = models.CharField(max_length=40)
    color = models.CharField(max_length=10)
    issue_type_id = models.CharField(max_length=40)
    issue_type_order = models.CharField(max_length=10)
    issue_type_project_id = models.CharField(max_length=40)


class TaigaIssue(models.Model):
    posted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='postedtaigaissues')
    subject = models.CharField(max_length=200)
    taiga_issue_type = models.ForeignKey(
        TaigaIssueType, null=True, on_delete=models.SET_NULL)
    description = models.TextField()
    posted = models.BooleanField(default=False)
    taiga_issue_id = models.IntegerField(null=True)

    def __str__(self):
        return self.subject


class TaigaIssueAttachment(models.Model):
    issue = models.ForeignKey(
        TaigaIssue, on_delete=models.CASCADE,
        related_name='attachments', null=True)
    attachment = models.ImageField(upload_to='taiga_issue_images')
