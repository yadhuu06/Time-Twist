"""
URL configuration for Watch_Shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  
    path('', include('UserAccounts.urls')),  
    path('admin_page/', include('AdminConsole.urls')),
    path('Brands/',include('brand.urls')),  
    path('catogory/', include('catogory.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('user_panel/', include('user_pannel.urls')),
    path('order_management/', include('order_management.urls')),
    path('coupon/',include('coupon.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)