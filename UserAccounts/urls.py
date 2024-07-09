from django.urls import path,include
from . import views

urlpatterns = [
    
    path('',views.signup,name='signup'),
    path('Register',views.Register,name='Register'),
    path('verify_otp',views.verify_otp,name='verify_otp'),
    path('login',views.login,name='login') 
]