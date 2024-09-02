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



def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.filter(is_active=True)
    user_address = UserAddress.objects.filter(user=request.user)

    # Check for out-of-stock items
    out_of_stock = False
    total_price = Decimal('0.00')
    for item in cart_items:
        if item.quantity > item.variant.variant_stock:
            out_of_stock = True
            messages.error(request, f"Insufficient stock for {item.variant.product.product_name} - {item.variant.variant_name}. Available stock is {item.variant.variant_stock}.")
            return redirect('cart:cart_view')

        item.variant_image = ProductVariantImages.objects.filter(product_variant=item.variant).first()
        total_price += item.sub_total()

    # Get eligible coupons
    coupons = Coupon.objects.filter(
        status=True, 
        expiry_date__gte=datetime.date.today(),
        minimum_amount__lte=total_price,
        maximum_amount__gte=total_price
    )
    user_used_coupons = UserCoupon.objects.filter(user=request.user, used=True).values_list('coupon_id', flat=True)
    available_coupons = coupons.exclude(id__in=user_used_coupons)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'user_address': user_address,
        'total_price': total_price,
        'coupons': available_coupons,
    }
    return render(request, 'UserSide/checkout.html', context)

@require_POST
def apply_coupon(request):
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

        discount_amount = min((total_price * coupon.discount) / 100, coupon.maximum_amount)
        new_total = total_price - discount_amount

        return JsonResponse({
            'success': True,
            'discount_amount': str(discount_amount),
            'new_total': str(new_total),
            'coupon_id': coupon.id
        })
    except Coupon.DoesNotExist:
        return JsonResponse({'error': 'Invalid coupon code or coupon not applicable.'}, status=400)



class CouponListView(View):
    def get(self, request):
        coupons = Coupon.objects.all()
        form = CouponForm()
        return render(request, 'coupons/coupon_list.html', {'coupons': coupons, 'form': form})

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
        coupon.delete()
        return JsonResponse({'success': True})
