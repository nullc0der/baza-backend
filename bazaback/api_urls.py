from django.urls import path, include
from bazaback.routers import router

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', include('userprofile.urls')),
    path('mock/', include('mockapi.urls')),
    path('proxc/', include('proxcdb.urls')),
    path('auth/', include('authclient.urls')),
    path('donate/', include('donation.urls')),
    path('purchasecoin/', include('coinpurchase.urls'))
]
