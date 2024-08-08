
from django.urls import path
from . import views

app_name = 'catogory'

urlpatterns = [
    path('', views.catogory_list, name='catogory_list'),
    path('add_catogory', views.add_catogory,name='add_catogory'),
    path('edit-category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('varient_list',views.varient_list,name='varient_list'),
    ]
