from django.urls import path,include
from . import views

urlpatterns = [
    
    # path('login_view',views.signup,name='signup'),
    path('Register',views.Register,name='Register'),
    path('verify_otp',views.verify_otp,name='verify_otp'),
    path('',views.login_view,name='login_view') ,
    path('home_view',views.home,name='home_view') ,
    path('google_login',views.google_login,name='google_login') 
]