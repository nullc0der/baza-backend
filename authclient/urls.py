from django.urls import path

from authclient import views


urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('register/', views.RegisterView.as_view()),
    path('validateemail/', views.ValidateEmailView.as_view()),
    path('isemailverified/', views.CheckEmailVerifiedView.as_view()),
    path('initiateforgotpassword/',
         views.InitiateForgotPasswordView.as_view()),
    path('forgotpassword/', views.ForgotPasswordView.as_view()),
    path('converttoken/', views.ConvertTokenView.as_view()),
    path('addemail/', views.AddUserEmailView.as_view()),
    path('twitter/getrequesttoken/', views.GetTwitterRequestCode.as_view()),
    path('twitter/login/', views.GetTwitterUserToken.as_view())
]
