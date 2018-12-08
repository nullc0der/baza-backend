from django.urls import path
from userprofile import views


urlpatterns = [
    path('', views.UserProfileView.as_view()),
    path('profilephotos/', views.UserProfilePhotoView.as_view()),
    path('photos/', views.UserPhotoView.as_view()),
    path('documents/', views.UserDocumentView.as_view()),
    path('phonenumbers/', views.UserPhoneView.as_view()),
    path('emails/', views.UserEmailView.as_view()),
    path('socialauths/', views.UserSocialView.as_view()),
    path('socialauths/connecttwitter/', views.ConnectTwitterView.as_view()),
    path('setpassword/', views.SetUserPasswordView.as_view()),
    path('twofactor/', views.UserTwoFactorView.as_view()),
    path('tasks/', views.GetUserTasks.as_view())
]
