from django.urls import path
from paypalpayment import views


urlpatterns = [
    path('createpayment/', views.CreatePaymentView.as_view()),
    path('executepayment/', views.ExecutePaymentView.as_view())
]
