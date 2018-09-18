from django.urls import path
from taigaissuecreator import views


urlpatterns = [
    path('', views.IssueView.as_view())
]
