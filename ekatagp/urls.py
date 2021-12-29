from django.urls import path

from ekatagp.views import PaymentSuccessWebhook

urlpatterns = [
    path('payment-success/', PaymentSuccessWebhook.as_view())
]
