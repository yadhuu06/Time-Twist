from django.urls import path
from .views import CouponListView, CouponCreateView, CouponUpdateView, CouponDeleteView, apply_coupon, generate_coupon_code

urlpatterns = [
    path('list/', CouponListView.as_view(), name='coupon_list'),
    path('create/', CouponCreateView.as_view(), name='coupon_create'),
    path('update/<int:pk>/', CouponUpdateView.as_view(), name='coupon_update'),
    path('delete/<int:pk>/', CouponDeleteView.as_view(), name='coupon_delete'),
    path('apply-coupon/', apply_coupon, name='apply_coupon'),
    path('generate-coupon-code/', generate_coupon_code, name='generate_coupon_code'),
]