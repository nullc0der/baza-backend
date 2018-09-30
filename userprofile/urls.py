from django.urls import path
from userprofile import views


urlpatterns = [
    path('', views.UserProfileView.as_view()),
    path('profilephotos/', views.UserProfilePhotoView.as_view()),
    path('photos/', views.UserPhotoView.as_view()),
    path('documents/', views.UserDocumentView.as_view()),
    path('phonenumbers/', views.UserPhoneView.as_view()),
    path('emails/', views.UserEmailView.as_view())
]
