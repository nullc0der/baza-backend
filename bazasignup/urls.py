from django.urls import path
from bazasignup import user_views
from bazasignup import staff_views


urlpatterns = [
    path('checksteps/', user_views.CheckCompletedTab.as_view()),
    path('userinfotab/', user_views.UserInfoTabView.as_view()),
    path('skipemail/', user_views.SkipEmailTabView.as_view()),
    path(
        'sendverificationcode/',
        user_views.InitiateEmailVerificationView.as_view()),
    path(
        'validateemailcode/',
        user_views.ValidateEmailVerificationCode.as_view()),
    path(
        'sendverificationcodeagain/',
        user_views.SendVerificationEmailAgain.as_view()),
    path('skipphone/', user_views.SkipPhoneTabView.as_view()),
    path(
        'sendphoneverificationcode/',
        user_views.InitiatePhoneVerificationView.as_view()),
    path(
        'validatesmscode/',
        user_views.ValidatePhoneVerificationCode.as_view()),
    path(
        'uploadsignupimage/',
        user_views.SignupImageUploadView.as_view()
    ),
    path(
        'toggledonor/',
        user_views.ToggleDonorView.as_view()
    ),
    path(
        'location/',
        user_views.LocationView.as_view()
    ),
    path(
        'signups/',
        staff_views.BazaSignupListView.as_view()
    ),
    path(
        'signup/<int:signup_id>/',
        staff_views.BazaSignupDetailsView.as_view()
    ),
    path(
        'signup/<int:signup_id>/userprofile/',
        staff_views.BazaSignupProfileDataView.as_view()
    ),
    path(
        'signup/<int:signup_id>/comments/',
        staff_views.BazaSignupCommentsView.as_view()
    ),
    path(
        'signup/<int:signup_id>/reset/',
        staff_views.BazaSignupResetView.as_view()
    ),
    path(
        'signup/staffbar/',
        staff_views.StaffBarView.as_view()
    ),
    path(
        'signup/loginoutstaff/',
        staff_views.StaffLoginLogoutView.as_view()
    ),
    path(
        'signup/reassignstaff/',
        staff_views.BazaSignupReassignStaffView.as_view()
    ),
    path(
        'signup/<int:signup_id>/activities/',
        staff_views.BazaSignupActivitiesView.as_view()
    )
]
