from django.urls import path

from hashtag import views

urlpatterns = [
    path('downloadsocialimage/', views.DownloadSocialPhotoView.as_view()),
    path('uploadimage/', views.UploadHashtagImageView.as_view())
]
