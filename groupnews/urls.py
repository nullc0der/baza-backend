from django.urls import path
from rest_framework.routers import DefaultRouter

from groupnews import views

urlpatterns = [
    path('uploadimage/', views.UploadImage.as_view())
]

router = DefaultRouter()
router.register(r'landingnews', views.SiteOwnerGroupNewsViewSets,
                basename='landingnews')
router.register(r'', views.NewsViewSets, basename='news')
urlpatterns += router.urls
