from django.urls import path
from userprofile import views


urlpatterns = [
    path('me/', views.WhoAmI.as_view())
]
