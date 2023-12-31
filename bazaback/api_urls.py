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
    path('issue/', include('taigaissuecreator.urls')),
    path('members/', include('publicusers.urls')),
    path('messenger/', include('messenger.urls')),
    path('groups/', include('group.urls')),
    path('notifications/', include('notifications.urls')),
    path('coinbase/', include('coinbasepay.urls')),
    path('hashtag/', include('hashtag.urls')),
    path('landing/', include('landing.urls')),
    path('faq/', include('groupfaq.urls')),
    path('userwebwallet/', include('webwallet.urls')),
    path('ekatagp/', include('ekatagp.urls'))
]
