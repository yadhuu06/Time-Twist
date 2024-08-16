from django.urls import path
from . import views
app_name= 'cart'
urlpatterns = [
    path('cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:id>/', views.add_cart, name='add_cart'),
     path('remove_cart_item/<int:id>/', views.remove_cart_item, name='remove_cart_item'),

]
