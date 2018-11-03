from django.urls import path, include
from bazaback.routers import router

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', include('userprofile.urls')),
    path('mock/', include('mockapi.urls')),
    path('proxc/', include('proxcdb.urls')),
    path('auth/', include('authclient.urls')),
    path('donate/', include('donation.urls')),
    path('purchasecoin/', include('coinpurchase.urls')),
    path('bazasignup/', include('bazasignup.urls')),
    path('landingcontact/', include('landingcontact.urls')),
    path('postissue/', include('taigaissuecreator.urls')),
    path('members/', include('publicusers.urls')),
    path('messenger/', include('messenger.urls')),
    path('groups/', include('group.urls'))
]
