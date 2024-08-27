from django.urls import path
from . import views

urlpatterns = [
    path('shop_view',views.shop_view,name='shop_view'),
    # path('edit_profile/',views.edit_profile,name='edit_profile'),
    path('add_address/', views.add_address, name='add_address'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('product_detail_user/<int:id>/',views.product_detail_user,name='product_detail_user'),
    path('user_profile',views.user_profile,name='user_profile'),
    path('checkout',views.checkout,name='checkout'),
    path('edit-profile/',views.edit_profile,name='edit-profile')
  
]
