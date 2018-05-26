from django.urls import path
from proxcdb.views import ProxcTransactionView


urlpatterns = [
    path('transactions/', ProxcTransactionView.as_view())
]
