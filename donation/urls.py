from django.urls import path

from donation import views

urlpatterns = [
    path('initiate/', views.InitiateDonationView.as_view()),
    path('initiate/anon/', views.InitiateAnonymousDonationView.as_view()),
    path('getlatest/', views.GetLatestDonations.as_view())
]
