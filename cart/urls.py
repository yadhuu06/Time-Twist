from django.urls import path
from . import views
app_name= 'cart'
urlpatterns = [
    path('cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:id>/', views.add_cart, name='add_cart'),
    path('remove_cart_item/<int:id>/', views.remove_cart_item, name='remove_cart_item'),
    path('update-cart-quantity/',views.update_cart_quantity, name='update_cart_quantity'),
     path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]
