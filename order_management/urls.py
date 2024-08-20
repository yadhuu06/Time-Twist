from django.urls import path,include
from . import views
app_name= 'order_management'
urlpatterns = [
  
    path('place_order',views.place_order,name='place_order'),
    path('my_orders',views.my_orders,name='my_orders')    
]