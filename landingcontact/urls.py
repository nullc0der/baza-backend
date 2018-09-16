from django.urls import path

from landingcontact import views


urlpatterns = [
    path('', views.LandingContactView.as_view())
]
