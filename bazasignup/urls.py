from django.urls import path
from bazasignup import views


urlpatterns = [
    path('checksteps/', views.CheckCompletedTab.as_view()),
    path('userinfotab/', views.UserInfoTabView.as_view()),
    path('skipemail/', views.SkipEmailTabView.as_view()),
    path(
        'sendverificationcode/',
        views.InitiateEmailVerificationView.as_view()),
    path(
        'validateemailcode/',
        views.ValidateEmailVerificationCode.as_view()),
    path(
        'sendverificationcodeagain/',
        views.SendVerificationEmailAgain.as_view())
]
