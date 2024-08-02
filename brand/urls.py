
from django.urls import path
from . import views
from django.urls import path
from . import views

app_name= 'brand'

urlpatterns = [
    path('', views.Brands_list, name='Brands'),
    path('add_brand/',views.add_brand,name='add_brand'),
    path('edit_brand/<int:brand_id>/',views.edit_brand,name='edit_brand')
]
