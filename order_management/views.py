from django.shortcuts import render, get_object_or_404,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from coupon.models import Coupon,UserCoupon
from user_pannel.models import UserAddress
from products.models import ProductVariant
from order_management.models import Order, Payment, OrderItem 
from django.http import HttpResponse
import uuid
from django.views.decorators.http import require_POST
from django.db import transaction
from decimal import Decimal
import datetime
from django.http import JsonResponse
import json




import razorpay
from django.conf import settings
from decimal import Decimal
import uuid
import datetime

def place_order(request):
    if request.method == 'POST':
        payment_method = request.POST.get('paymentMethod')
        address_id = request.POST.get('address')

        if not payment_method or not address_id:
            messages.error(request, 'Please select both a payment method and a delivery address.')
            return redirect('checkout')

        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.filter(is_active=True)
        total_price = sum(item.sub_total() for item in cart_items)

        if payment_method == 'razorpay':
            print("razopay")
            
            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

            razorpay_order = razorpay_client.order.create({
                'amount': int(total_price * 100),  
                'currency': 'INR',
                'payment_capture': '1' 
            })

            request.session['razorpay_order_id'] = razorpay_order['id']

            return render(request, 'UserSide/razorpay_payment.html', {
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_API_KEY,
                'amount': total_price,
                'user': request.user,
                'address_id': address_id,
                'cart_items': cart_items,
                'total_price': total_price,
            })

        if payment_method == 'cashOnDelivery' and total_price >= 15000:
            messages.error(request, 'Cash on Delivery is not available for orders over Rs 15,000.')
            return redirect('checkout')

        try:
            selected_address = UserAddress.objects.get(id=address_id, user=request.user)
        except UserAddress.DoesNotExist:
            messages.error(request, 'Selected address is invalid.')
            return redirect('checkout')

        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('checkout')

        for item in cart_items:
            product_variant = item.variant
            if not product_variant.is_active:
                messages.error(request, f'Product {product_variant.product_name} is no longer available.')
                return redirect('checkout')
            if product_variant.variant_stock < item.quantity:
                messages.error(request, f'Insufficient stock for {product_variant.product_name}.')
                return redirect('checkout')

        coupon_id = request.POST.get('applied_coupon')
        discount_amount = Decimal('0.00')
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                if total_price >= coupon.minimum_amount and total_price <= coupon.maximum_amount:
                    discount_amount = min((total_price * coupon.discount) / 100, coupon.maximum_amount)
                    total_price -= discount_amount
                else:
                    messages.error(request, "Coupon not applicable for this order amount.")
                    return redirect('checkout')
            except Coupon.DoesNotExist:
                messages.error(request, "Invalid coupon.")
                return redirect('checkout')

        payment = Payment.objects.create(
            method=payment_method,
            user=request.user,
            amount=total_price
        )

        order = Order.objects.create(
            user=request.user,
            address=selected_address,
            order_id=str(uuid.uuid4()),
            payment=payment,
            total_price=total_price + discount_amount,
            offer_price=discount_amount,
            final_price=total_price,
            status='Pending'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_variant=item.variant,
                quantity=item.quantity,
                price=item.variant.offer_price
            )
            item.variant.variant_stock -= item.quantity
            item.variant.save()
            item.delete()

        if coupon_id:
            UserCoupon.objects.create(
                user=request.user,
                coupon_id=coupon_id,
                used=True,
                used_at=datetime.datetime.now(),
                order=order
            )

        messages.success(request, 'Order placed successfully!')
        return render(request, 'UserSide/order_placed.html', {'order': order})

    return redirect('checkout')

    
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
import razorpay
import json
import hmac
import hashlib

def verify_payment(request):
    if request.method == 'POST':
        print("this is razorpay call back")
        razorpay_order_id = request.POST.get('razorpay_order_id')
        payment_id = request.POST.get('razorpay_payment_id')
        signature = request.POST.get('razorpay_signature')

        if not all([razorpay_order_id, payment_id, signature]):
            messages.error(request, 'Missing payment details.')
            return redirect('checkout')

        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        try:
            client.utility.verify_payment_signature(params_dict)
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            print("order")
            order.status = 'Completed'          
            order.save()
            print("success")
            messages.success(request, 'Payment successful and order confirmed!')
            return render(request, 'UserSide/order_placed.html', {'order': order})
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
            return redirect('checkout')

    messages.error(request, 'Invalid request.')
    return redirect('checkout')

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import razorpay
import hmac
import hashlib
from .models import Order

@csrf_exempt
def razorpay_callback(request):
    if request.method == 'POST':
        try:
            # Extract data from request
            payload = request.body.decode('utf-8')
            signature = request.headers.get('X-Razorpay-Signature')
            
            # Verify signature
            client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
            is_valid = client.utility.verify_webhook_signature(payload, signature, settings.RAZORPAY_API_SECRET)
            
            if is_valid:
                data = json.loads(payload)
                order_id = data['payload']['payment']['entity']['order_id']
                payment_id = data['payload']['payment']['entity']['id']
                status = data['event']

                # Update order status
                try:
                    order = Order.objects.get(razorpay_order_id=order_id)
                    if status == 'payment.captured':
                        order.status = 'Completed'
                        order.save()
                    elif status == 'payment.failed':
                        order.status = 'Failed'
                        order.save()
                except Order.DoesNotExist:
                    pass  # Handle the case where the order doesn't exist

                return JsonResponse({'status': 'ok'})
            else:
                return JsonResponse({'status': 'invalid signature'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'invalid method'}, status=405)



def calculate_cart_total(user):
    cart_items = CartItem.objects.filter(cart__user=user, is_active=True)
    return sum(item.variant.price * item.quantity for item in cart_items)
   
   
   
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product_variant').order_by('-id')
    return render(request, 'UserSide/my_orders.html', {'orders': orders})



def order_details_admin(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'AdminSide/order_details.html', {'order': order})


@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    if order.status != 'Pending':
        messages.error(request, "Order cannot be canceled.")
        return redirect('order_management:order_detail', order_id=order_id)

    try:
        with transaction.atomic():
            for item in order.items.all():
                product_variant = item.product_variant
                product_variant.variant_stock += item.quantity
                product_variant.save()

            order.status = 'Canceled'
            order.save()

        messages.success(request, "Order canceled successfully.")
    except Exception as e:
        messages.error(request, f"An error occurred while canceling the order: {str(e)}")
    
    return redirect('order_management:my_orders')


def change_status(request, order_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            order = get_object_or_404(Order, id=order_id)

            if new_status:
                order.status = new_status
                order.save()
                return JsonResponse({'success': True, 'status': new_status})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)