
from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_page, name='admin_page'),
    path('admin_login/', views.admin_login, name='admin_login'),
]

