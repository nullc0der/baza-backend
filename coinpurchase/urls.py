from django.urls import path

from coinpurchase import views


urlpatterns = [
    path('coinvalue/', views.GetCoinValue.as_view()),
    path('totalpurchased/', views.GetTotalCoinPurchased.as_view())
]
