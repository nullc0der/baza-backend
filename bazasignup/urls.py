from django.urls import path
from bazasignup import views


urlpatterns = [
    path('checksteps/', views.CheckCompletedTab.as_view()),
    path('userinfotab/', views.UserInfoTabView.as_view())
]
