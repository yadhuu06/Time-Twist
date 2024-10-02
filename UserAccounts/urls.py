from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    
    # path('login_view',views.signup,name='signup'),
    path('Register/', views.Register, name='Register'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('home/', views.home_view, name='home_view'),
    path('', views.login_view, name='login_view'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_change_view, name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='UserSide/user-login/password_reset_complete.html'), name='password_reset_complete'),  # Add this


   
]