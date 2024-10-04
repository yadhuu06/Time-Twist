# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('list/', views.products_list, name='products_list'),
    path('add/', views.add_products, name='add_products'), 
    path('Varient/<int:Products_id>/', views.list_productVarient, name='list_productVarient'), 
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('New/Varient/<int:Products_id>/', views.add_productVarient, name='add_productVarient'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'), 
    path('edit_variant/<int:variant_id>/', views.edit_productVariant, name='edit_productVariant'),
    
   
    
    ] 
