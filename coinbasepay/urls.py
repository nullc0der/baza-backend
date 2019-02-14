from django.urls import path
from coinbasepay import views

urlpatterns = [
    path('initiate/<str:charge_type>/',
         views.IntializeCoinbaseChargeView.as_view()),
    path('webhook/', views.CoinbaseWebhookView.as_view())
]
