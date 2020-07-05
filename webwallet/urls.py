from django.urls import path

from webwallet import views


urlpatterns = [
    path('', views.UserWebWalletView.as_view()),
    path('details/', views.UserWebWalletDetailsView.as_view()),
    path('send/', views.UserWebWalletTxView.as_view())
]
