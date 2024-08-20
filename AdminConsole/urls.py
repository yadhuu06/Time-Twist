
from django.urls import path
from . import views

urlpatterns = [
    path('admin_page/', views.admin_page, name='admin_page'),
    path('', views.admin_login, name='admin_login'),
    path('users_list/', views.users_list, name='users_list'),
    path('documentaion/', views.documentaion, name='documentaion'),
    path('Block_user/', views.Block_user, name='Block_user'),
    path('admin_order_list', views.admin_order_list, name='admin_order_list'),
    path('orders/change-status/<int:order_id>/', views.change_order_status, name='change_order_status')
]

