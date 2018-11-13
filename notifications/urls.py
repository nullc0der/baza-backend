from django.urls import path

from notifications import views

urlpatterns = [
    path('', views.NotificationView.as_view()),
    path('setread/', views.NotificationDetailView.as_view())
]
