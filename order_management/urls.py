from django.urls import path
from . import views

app_name = 'order_management'

urlpatterns = [
    path('place_order', views.place_order, name='place_order'),
    path('my_orders', views.my_orders, name='my_orders'),
    path('order_details/<str:order_id>/', views.order_details_admin, name='order_details-admin'),
    path('order_details-user/<str:order_id>/', views.order_details_user, name='order_details_user'),
    path('order/cancel/<str:order_id>/', views.cancel_order, name='cancel_order'),
    path('change-status/<int:order_id>/', views.change_status, name='change_status'),
    path('payment/verify/', views.verify_payment, name='payment_verify'),
    path('return-order/<str:order_id>/', views.return_order, name='return_order'),
    path('submit-rating/<int:product_id>/', views.submit_rating, name='submit_rating'),

  

]
