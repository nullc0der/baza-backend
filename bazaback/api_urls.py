from django.urls import path, include
from bazaback.routers import router

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_auth.urls')),
    path('auth/registration/', include('rest_auth.registration.urls')),
    path('mock/', include('mockapi.urls'))
]
