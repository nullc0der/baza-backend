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
        views.SendVerificationEmailAgain.as_view()),
    path('skipphone/', views.SkipPhoneTabView.as_view()),
    path(
        'sendphoneverificationcode/',
        views.InitiatePhoneVerificationView.as_view()),
    path(
        'validatesmscode/',
        views.ValidatePhoneVerificationCode.as_view()),
    path(
        'sendphoneverificationcodeagain/',
        views.SendVerificationSMSAgain.as_view()),
    path(
        'uploadsignupimage/',
        views.SignupImageUploadView.as_view()
    ),
    path(
        'signups/',
        views.BazaSignupListView.as_view()
    ),
    path(
        'signup/<int:signup_id>/',
        views.BazaSignupDetailsView.as_view()
    )
]
