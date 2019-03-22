from django.urls import path
from rest_framework.routers import DefaultRouter

from groupnews import views

urlpatterns = [
    path('uploadimage/', views.UploadImage.as_view())
]

router = DefaultRouter()
router.register(r'landingnews', views.SiteOwnerGroupNewsViewSets,
                base_name='landingnews')
router.register(r'', views.NewsViewSets, base_name='news')
urlpatterns += router.urls
