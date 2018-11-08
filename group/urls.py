from django.urls import path

from group import views


urlpatterns = [
    path('', views.GroupsView.as_view()),
    path('<int:group_id>/', views.GroupDetailView.as_view()),
    path('create/', views.CreateGroupView.as_view()),
    path('<int:group_id>/members/', views.GroupMembersView.as_view()),
    path('<int:group_id>/members/changerole/',
         views.GroupMemberChangeRoleView.as_view()),
]
