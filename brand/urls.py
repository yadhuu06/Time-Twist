
from django.urls import path
from . import views
# urls.py
from django.urls import path
from . import views



urlpatterns = [
    path('', views.Brands_list, name='Brands'),
    path('add_brand/',views.add_brand,name='add_brand'),
    path('edit_brand/<int:brand_id>/',views.edit_brand,name='edit_brand')
]
