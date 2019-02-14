from django.urls import path, include

from group import views


urlpatterns = [
    path('', views.GroupsView.as_view()),
    path('siteownergroup/', views.SiteOwnerGroupView.as_view()),
    path('<int:group_id>/', views.GroupDetailView.as_view()),
    path('create/', views.CreateGroupView.as_view()),
    path('<int:group_id>/members/', views.GroupMembersView.as_view()),
    path('<int:group_id>/members/changerole/',
         views.GroupMemberChangeRoleView.as_view()),
    path('<int:group_id>/notifications/',
         views.GroupNotificationsView.as_view()),
    path('<int:group_id>/subscribe/', views.GroupSubscribeView.as_view()),
    path('<int:group_id>/join/', views.JoinGroupView.as_view()),
    path('<int:group_id>/joinrequests/', views.GroupJoinRequestView.as_view()),
    path('<int:group_id>/mynotifications/',
         views.GroupMemberNotificationView.as_view()),
    path('<int:group_id>/invitemember/',
         views.InviteMemberView.as_view()),
    path('inviteaction/', views.InviteAction.as_view()),
    path('posts/', include('grouppost.urls'))
]
