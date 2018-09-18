from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class TaigaIssue(models.Model):
    posted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='postedtaigaissues')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    posted = models.BooleanField(default=False)
    taiga_issue_id = models.IntegerField(null=True)

    def __str__(self):
        return self.subject


class TaigaIssueAttachment(models.Model):
    issue = models.ForeignKey(
        TaigaIssue, on_delete=models.CASCADE,
        related_name='attachments', null=True)
    attachment = models.ImageField()
