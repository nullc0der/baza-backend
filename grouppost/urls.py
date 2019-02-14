from django.urls import path
from rest_framework.routers import DefaultRouter

from grouppost import views

urlpatterns = [
    path('uploadimage/', views.UploadImage.as_view())
]

router = DefaultRouter()
router.register(r'comment', views.CommentViewset, base_name='comment')
router.register(r'', views.PostViewSets, base_name='post')
urlpatterns += router.urls
