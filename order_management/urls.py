from django.urls import path
from . import views

app_name = 'order_management'

urlpatterns = [
    path('place_order', views.place_order, name='place_order'),
    path('my_orders', views.my_orders, name='my_orders'),
    path('order_details/<uuid:order_id>/', views.order_details_admin, name='order_details-admin'),
    path('order/cancel/<uuid:order_id>/', views.cancel_order, name='cancel_order'),
]
