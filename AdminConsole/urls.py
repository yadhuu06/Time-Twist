
from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_page, name='admin_page'),
    path('admin_page/', views.admin_login, name='admin_login'),
    path('users_list/', views.users_list, name='users_list'),
    path('documentaion/', views.documentaion, name='documentaion'),
     path('Block_user/', views.Block_user, name='Block_user'),
]

