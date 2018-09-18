from django import forms


class TaigaIssueForm(forms.Form):
    subject = forms.CharField(max_length=200)
    description = forms.CharField(required=False)
