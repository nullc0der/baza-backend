from django.urls import path

from coinpurchase import views


urlpatterns = [
    #    path('', views.ProcessCoinPurchase.as_view()),
    path('coinvalue/', views.GetCoinValue.as_view()),
    path('totalpurchased/', views.GetTotalCoinPurchased.as_view())
]
