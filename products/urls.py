# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('list/', views.products_list, name='products_list'),
    path('add/', views.add_products, name='add_products'), 
    path('Varient/<int:Products_id>/', views.add_productVarient, name='add_productVarient'), 
    path('products/product_detail/<int:Products_id>/',views.product_detail, name='product_detail'),
     
    ] 
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
