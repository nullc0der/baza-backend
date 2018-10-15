from django.urls import path
from publicusers import views


urlpatterns = [
    path('', views.UsersListView.as_view())
]
