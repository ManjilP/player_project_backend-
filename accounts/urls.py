from django.urls import path
from accounts import views

from knox.views import LogoutView, LogoutAllView

app_name = 'accounts'

urlpatterns = [
   path('login/', views.LoginAPIView.as_view(), name='login'),
   path('logout/', LogoutView.as_view(), name='logout'),
   path('logout/all/', LogoutAllView.as_view(), name='logout_all'),

   path('password/change/', views.ChangePasswordAPIView.as_view(), name='change_password'),
   path('password/forget/', views.ForgotPasswordRequestAPIView.as_view(), name='forgot_password'),
   path('validate/otp/', views.ValidateOTPView.as_view(), name='validate_otp'),
   path('password/reset/<str:uid>/<str:token>/', views.ResetPasswordView.as_view(), name='reset_password'),

   path('register/', views.UserRegisterCreateAPIView.as_view(), name='user_register'),

   path('manager/invite/', views.InviteNewManagerAPIView.as_view(), name='invite_manager'),
   path('register/manager/invited/<str:encoded_email>/', views.RegisterInvitedManagerAPIView.as_view(), name='register_manager'),

   path('user/edit/', views.EditProfileAPIView.as_view(), name='user_update'),
]