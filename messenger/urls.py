from django.urls import path
from messenger import views


urlpatterns = [
    path('chatrooms/', views.ChatRoomsView.as_view()),
    path('chat/<int:chat_id>/', views.ChatRoomDetailsView.as_view()),
    path('deletemessages/', views.DeleteMessageView.as_view()),
    path('deletechatrooms/', views.DeleteChatRoomView.as_view()),
    path('updatemessagestatus/', views.UpdateReadStatusView.as_view())
]
