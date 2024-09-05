# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import  Coupon, UserCoupon
from products.models import ProductVariantImages
from cart.models import Cart, CartItem
from user_pannel.models import UserAddress
from  order_management.models import Order, OrderItem, Payment
from decimal import Decimal
import datetime
import uuid
from django.views import View
from .models import Coupon
from .forms import CouponForm





@require_POST
def apply_coupon(request):
    print("aagaya")
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        total_price = Decimal(request.POST.get('total_price', '0'))

        try:
            coupon = Coupon.objects.get(
                coupon_code=coupon_code,
                status=True,
                expiry_date__gte=datetime.date.today(),
                minimum_amount__lte=total_price,
                maximum_amount__gte=total_price
            )
            
            if UserCoupon.objects.filter(user=request.user, coupon=coupon, used=True).exists():
                return JsonResponse({'error': 'You have already used this coupon.'}, status=400)
            discount_amount = (total_price * coupon.discount) / 100
            new_total = total_price - discount_amount

            return JsonResponse({
                'success': True,
                'discount_amount': str(discount_amount),
                'new_total': str(new_total),
                'coupon_id': coupon.id
            })

        except Coupon.DoesNotExist:

            return JsonResponse({'error': 'Invalid coupon code or coupon not applicable.'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)




class CouponListView(View):
    def get(self, request):
        coupons = Coupon.objects.all()
        return render(request, 'AdminSide/coupon_list.html', {'coupons': coupons})

class CouponCreateView(View):
    def post(self, request):
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save()
            return JsonResponse({
                'id': coupon.id,
                'coupon_name': coupon.coupon_name,
                'coupon_code': coupon.coupon_code,
                'discount': coupon.discount,
                'minimum_amount': coupon.minimum_amount,
                'maximum_amount': coupon.maximum_amount,
                'expiry_date': coupon.expiry_date.strftime('%Y-%m-%d'),
                'status': coupon.status,
            })
        return JsonResponse({'errors': form.errors}, status=400)



class CouponUpdateView(View):
    def post(self, request, pk):
        coupon = get_object_or_404(Coupon, pk=pk)
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            coupon = form.save()
            return JsonResponse({
                'id': coupon.id,
                'coupon_name': coupon.coupon_name,
                'coupon_code': coupon.coupon_code,
                'discount': coupon.discount,
                'minimum_amount': coupon.minimum_amount,
                'maximum_amount': coupon.maximum_amount,
                'expiry_date': coupon.expiry_date.strftime('%Y-%m-%d'),
                'status': coupon.status,
            })
        return JsonResponse({'errors': form.errors}, status=400)

class CouponDeleteView(View):
  
    def post(self, request, pk):
        coupon = get_object_or_404(Coupon, pk=pk)
        coupon.status = False
        coupon.save()

def generate_coupon_code(request):
    coupon_code = str(uuid.uuid4()).upper()[:8]
    return JsonResponse({'coupon_code': coupon_code})
