from django.conf import settings

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from taigaissuecreator.forms import TaigaIssueForm
from taigaissuecreator.tasks import task_post_issue
from taigaissuecreator.models import TaigaIssueAttachment


class IssueView(views.APIView):
    """
    This api will be used for posting an issue by an user
    TODO: Change form to serializer
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        issue_form = TaigaIssueForm(request.POST)
        if issue_form.is_valid():
            attachments_ids = []
            files = request.FILES.getlist('attachments', None)
            if files and len(files) > 5:
                return Response(
                    {
                        'attachments':
                        "This field can contain maximum 5 files",
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            for file in files:
                taigaissueattachment = TaigaIssueAttachment.objects.create(
                    attachment=file
                )
                attachments_ids.append(taigaissueattachment.id)
            task_post_issue.delay(
                posted_by_id=request.user.id,
                subject=issue_form.cleaned_data.get('subject'),
                description=issue_form.cleaned_data.get('description'),
                attachments_ids=attachments_ids
            )
            return Response()
        return Response(
            issue_form.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
