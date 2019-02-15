from django.urls import path

from donation import views

urlpatterns = [
    path('initiate/', views.InitiateDonationView.as_view()),
    path('initiate/anon/', views.InitiateAnonymousDonationView.as_view()),
    path('getlatest/', views.GetLatestDonations.as_view()),
    path('getstats/', views.GetDonationStats.as_view()),
    path('donors/', views.GetTotalDonors.as_view())
]