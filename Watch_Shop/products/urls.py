# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.products_list, name='products_list'),
    path('add/', views.add_products, name='add_products'), 
    path('Varient/<int:Prodcuts_id>/', views.add_productVarient, name='add_productVarient'), 
     
    ]
