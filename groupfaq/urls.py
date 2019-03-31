from django.urls import path
from groupfaq import views


urlpatterns = [
    path('upload/', views.UploadFaqJSON.as_view()),
    path('download/', views.DownloadFaqJSON.as_view())
]
