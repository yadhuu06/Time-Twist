from django.urls import path,include
from . import views

urlpatterns = [
    
    path('',views.signup,name='signup'),
    path('Register',views.Register,name='Register'),
    # path('Otp',views.Otp,name='Otp'),
]