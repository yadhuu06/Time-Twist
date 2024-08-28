from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Coupon
from .forms import CouponForm
from django.views import View
import random
import string

# Coupon list view
class CouponListView(View):
    def get(self, request):
        coupons = Coupon.objects.all()
        form = CouponForm()
        return render(request, 'AdminSide/coupon_list.html', {'coupons': coupons, 'form': form})

# Coupon create view
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

# Coupon update view
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

# Coupon delete view
class CouponDeleteView(View):
    def post(self, request, pk):
        coupon = get_object_or_404(Coupon, pk=pk)
        coupon.delete()
        return JsonResponse({'success': True})


class GenerateCouponCodeView(View):
    def get(self, request):
        code = self.generate_coupon_code()
        return JsonResponse({'coupon_code': code})

    def generate_coupon_code(self):
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(8))
