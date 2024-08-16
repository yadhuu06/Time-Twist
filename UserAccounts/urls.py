from django.urls import path,include
from . import views

urlpatterns = [
    
    # path('login_view',views.signup,name='signup'),
    path('Register',views.Register,name='Register'),
    path('verify_otp',views.verify_otp,name='verify_otp'),
    path('home/',views.home_view, name='home_view'),
    path('',views.login_view, name='login_view'),
    path('resend_otp',views.resend_otp,name='resend_otp'),
    path('logout',views.logout_view,name='logout'),
    
]