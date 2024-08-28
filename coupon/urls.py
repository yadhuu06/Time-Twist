from django.urls import path
from .views import CouponListView, CouponCreateView, CouponUpdateView, CouponDeleteView, GenerateCouponCodeView

urlpatterns = [
    path('coupons/', CouponListView.as_view(), name='coupon_list'),
    path('coupons/create/', CouponCreateView.as_view(), name='coupon_create'),
    path('coupons/<int:pk>/update/', CouponUpdateView.as_view(), name='coupon_update'),
    path('coupons/<int:pk>/delete/', CouponDeleteView.as_view(), name='coupon_delete'),
    path('coupons/generate-code/', GenerateCouponCodeView.as_view(), name='generate_coupon_code'),
]
