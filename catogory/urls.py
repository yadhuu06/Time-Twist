# catogory/urls.py

from django.urls import path
from . import views

app_name = 'catogory'

urlpatterns = [
    path('', views.catogory_list, name='catogory_list'),
    path('add_catogory',views.add_catogory,name='add_catogory')
    
]
