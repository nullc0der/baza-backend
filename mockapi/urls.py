from django.urls import path
from mockapi import views

urlpatterns = [
    path('walletaccounts/', views.WalletAccounts.as_view()),
    path('wallettransactions/', views.WalletTransaction.as_view())
]
