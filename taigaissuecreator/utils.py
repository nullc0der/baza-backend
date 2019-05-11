import requests
import json
from django.conf import settings
from django.contrib.auth.models import User

from taigaissuecreator.models import (
    TaigaIssue, TaigaIssueAttachment, TaigaIssueType)

API_BASE_URL = 'https://' + settings.TAIGA_HOST + '/api/v1'
LOGIN_URL = API_BASE_URL + '/auth'
ISSUE_URL = API_BASE_URL + '/issues'
ISSUE_TYPE_URL = API_BASE_URL + '/issue-types'
ATTACHMENT_URL = ISSUE_URL + '/attachments'


def get_auth_token():
    """ Returns auth_token if success else None """
    data = {
        'username': settings.TAIGA_USERNAME,
        'password': settings.TAIGA_PASSWORD,
        'type': 'normal'
    }
    login_res = requests.post(LOGIN_URL, data=data)
    if login_res.status_code == 200:
        res_data = json.loads(login_res.content)
        if res_data['auth_token']:
            return res_data['auth_token']
    return None


def get_issue_types():
    issue_types = []
    auth_token = get_auth_token()
    headers = {
        "Authorization": "Bearer " + auth_token
    }
    data = {
        'project': 9
    }
    res = requests.get(ISSUE_TYPE_URL, headers=headers, data=data)
    if res.status_code == 200:
        issue_types = res.json()
        for issue_type in issue_types:
            TaigaIssueType.objects.get_or_create(
                name=issue_type['name'],
                color=issue_type['color'],
                issue_type_id=issue_type['id'],
                issue_type_order=issue_type['order'],
                issue_type_project_id=issue_type['project']
            )
    return issue_types


def post_issue(
        posted_by_id, subject, description, attachments_ids,
        issue_type_id=None):
    taiga_issue_type = None
    if issue_type_id:
        try:
            taiga_issue_type = TaigaIssueType.objects.get(
                issue_type_id=issue_type_id)
        except TaigaIssueType.DoesNotExist:
            pass
    posted_by = User.objects.get(id=posted_by_id)
    auth_token = get_auth_token()
    taigaissue = TaigaIssue(
        posted_by=posted_by,
        subject=subject,
        description=description,
        taiga_issue_type=taiga_issue_type
    )
    # public_profile_chunk = posted_by.profile.get_public_profile_url().split(
    #     '/')[2:]
    # public_profile = \
    #     "https://development.ekata.social/"\
    #     + '/'.join(public_profile_chunk)
    extra_info = \
        '\n\n\n####Extra Info\n {0} posted by: {1}\n User ID: {2}'.format(
            taiga_issue_type.name if taiga_issue_type else 'Issue',
            posted_by.username,
            posted_by.id
        )
    if auth_token:
        headers = {
            "Authorization": "Bearer " + auth_token
        }
        data = {
            'subject': subject,
            'description': description + extra_info,
            'type': taiga_issue_type.issue_type_id
            if taiga_issue_type else None,
            'project': 9
        }
        issue_res = requests.post(ISSUE_URL, headers=headers, data=data)
        issue_res_data = json.loads(issue_res.content)
        taigaissue.taiga_issue_id = issue_res_data.get('id', None)
        # HACK: to prevent ValueError, investigate more on this
        taigaissue.save()
        if 'id' in issue_res_data and attachments_ids:
            for attachment_id in attachments_ids:
                post_attachment(
                    auth_token, issue_res_data['id'],
                    attachment_id, taigaissue)
        taigaissue.posted = True
    taigaissue.save()


def post_attachment(token, object_id, attachment_id, taigaissue):
    headers = {
        "Authorization": "Bearer " + token
    }
    data = {
        'object_id': object_id,
        'project': 9
    }
    taigaissueattachment = TaigaIssueAttachment.objects.get(id=attachment_id)
    files = {
        'attached_file': taigaissueattachment.attachment
    }
    requests.post(
        ATTACHMENT_URL, headers=headers, data=data, files=files)
    taigaissueattachment.issue = taigaissue
    taigaissueattachment.save()
