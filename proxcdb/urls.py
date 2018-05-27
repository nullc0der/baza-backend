from django.urls import path
from proxcdb import views


urlpatterns = [
    path('transactions/', views.ProxcTransactionView.as_view()),
    path('users/', views.proxcdb_account_autocomplete)
]
