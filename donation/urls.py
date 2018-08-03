from django.urls import path

from donation import views

urlpatterns = [
    path('', views.DonationView.as_view()),
    path('anon/', views.AnonymousDonationView.as_view())
]
