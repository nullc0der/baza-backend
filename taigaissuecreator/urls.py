from django.urls import path
from taigaissuecreator import views


urlpatterns = [
    path('create/', views.IssueView.as_view()),
    path('gettypes/', views.IssueTypeView.as_view())
]
