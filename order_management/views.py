from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.template.loader import get_template
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from order_management.models import Order, Payment, OrderItem, OrderAddress, Return
from cart.models import Cart, CartItem, Wallet, WalletTransaction
from coupon.models import Coupon, UserCoupon
from user_pannel.models import UserAddress
from products.models import ProductVariant,ProductRating
from user_pannel.decorators import active_user_required
from django.core.paginator import Paginator
from datetime import timedelta
from decimal import Decimal
import datetime
import razorpay
import hashlib
from AdminConsole.views import is_admin
import uuid
import json
import hmac



@active_user_required
@never_cache
def place_order(request):
    print("place order")
    if request.method == 'POST':
        payment_method = request.POST.get('paymentMethod')
        address_id = request.POST.get('address')
        applied_coupon_id = request.POST.get('applied_coupon')
      
        

        if not payment_method or not address_id:
            messages.error(request, 'Please select both a payment method and a delivery address.')
            return redirect('checkout')

        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.filter(is_active=True)
        total_price = sum(item.sub_total() for item in cart_items)
        main_total = sum(item.main_total() for item in cart_items)

        coupon_discount = 0
        if applied_coupon_id:
            coupon = get_object_or_404(Coupon, coupon_code=applied_coupon_id, status=True)
            if coupon.minimum_amount <= total_price <= coupon.maximum_amount:
                coupon_discount = (total_price * coupon.discount) / 100
                total_price -= coupon_discount
        
        
        shipping_charge = 0        
        if total_price < 10000:
            shipping_charge = 40
            total_price += shipping_charge 

        for item in cart_items:
            product_variant = item.variant
            product = product_variant.product

          
            if not product.is_active:
                messages.error(request, f'Product {product.product_name} is no longer available.')
                return redirect('checkout')
            if not product_variant.is_active:
                messages.error(request, f'Variant {product_variant.variant_name} for product {product.product_name} is no longer available.')
                return redirect('checkout')
            if product_variant.variant_stock < item.quantity:
                messages.error(request, f'Insufficient stock for {product_variant.variant_name} of product {product.product_name}.')
                return redirect('checkout')

        selected_address = get_object_or_404(UserAddress, id=address_id, user=request.user)

        
        if not request.user.is_active:
            messages.error(request, 'Your account is not active.')
            return redirect('checkout')

        with transaction.atomic():
            if payment_method == 'razorpay':
                razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
                razorpay_order = razorpay_client.order.create({
                    'amount': int(total_price * 100), 
                    'currency': 'INR',
                    'payment_capture': '1'  
                })

                request.session['razorpay_order_id'] = razorpay_order['id']
             

                
                order = Order.objects.create(
                    user=request.user,
                    address=selected_address,
                    order_id=razorpay_order['id'],
                    
                    total_price=main_total,
                    offer_price=coupon_discount,
                    shipping=shipping_charge,
                    final_price=total_price,
                    
                )
                payment = Payment.objects.create(
                method='razorpay',
                user=order.user,
                amount=order.final_price,
                status='Failed')
                order.payment=payment
                payment.save()

                OrderAddress.objects.create(
                    user=request.user,
                    name=selected_address.name,
                    house_name=selected_address.house_name,
                    street_name=selected_address.street_name,
                    pin_number=selected_address.pin_number,
                    district=selected_address.district,
                    state=selected_address.state,
                    phone_number=selected_address.phone_number
                )

                for item in cart_items:
                    item_discount = (item.sub_total() / (total_price + coupon_discount)) * coupon_discount
                    OrderItem.objects.create(
                        order=order,
                        product_variant=item.variant,
                        quantity=item.quantity,
                        price=item.variant.offer_price,
                        coupon_offer=item_discount,
                        paid_price=item.variant.offer_price - item_discount
                    )
                    item.variant.variant_stock -= item.quantity
                    item.variant.save()

                if applied_coupon_id:
                    UserCoupon.objects.create(
                        user=request.user,
                        coupon=coupon,
                        used=True,
                        used_at=timezone.now(),
                        order=order
                    )

                return render(request, 'UserSide/razorpay_payment.html', {
                    'razorpay_order_id': razorpay_order['id'],
                    'razorpay_key_id': settings.RAZORPAY_API_KEY,
                    'amount': total_price,
                    'user': request.user,
                    'address_id': address_id,
                })

            elif payment_method == 'cashOnDelivery':
                if total_price >= 10000:
                    messages.error(request, 'Cash on Delivery is not available for orders over Rs 10,000.')
                    return redirect('checkout')

                payment = Payment.objects.create(
                    method=payment_method,
                    user=request.user,
                    amount=total_price
                )
                
                order = Order.objects.create(
                    user=request.user,
                    address=selected_address,
                    payment=payment,
                    order_id=str(uuid.uuid4()),
                    total_price=main_total,
                    offer_price=coupon_discount,
                    final_price=total_price,
                    shipping=shipping_charge,                   
                    status='Pending'
                )

                OrderAddress.objects.create(
                    user=request.user,
                    name=selected_address.name,
                    house_name=selected_address.house_name,
                    street_name=selected_address.street_name,
                    pin_number=selected_address.pin_number,
                    district=selected_address.district,
                    state=selected_address.state,
                    phone_number=selected_address.phone_number
                )

                for item in cart_items:
                    item_discount = (item.sub_total() / (total_price + coupon_discount)) * coupon_discount
                    OrderItem.objects.create(
                        order=order,
                        product_variant=item.variant,
                        quantity=item.quantity,
                        price=item.variant.offer_price,
                        coupon_offer=item_discount,
                        paid_price=item.variant.offer_price - item_discount
                    )
                    item.variant.variant_stock -= item.quantity
                    item.variant.save()

                if applied_coupon_id:
                    UserCoupon.objects.create(
                        user=request.user,
                        coupon=coupon,
                        used=True,
                        used_at=timezone.now(),
                        order=order
                    )

                cart.items.all().delete()

                messages.success(request, 'Order placed successfully!')
                return render(request, 'UserSide/order_placed.html', {'order': order})

            elif payment_method == 'Wallet':
                wallet = get_object_or_404(Wallet, user=request.user)
                if wallet.balance >= total_price:
                    wallet.balance -= total_price
                    wallet.updated_at = timezone.now()
                    wallet.save()

                    WalletTransaction.objects.create(
                        wallet=wallet,
                        amount=total_price,
                        description=f"Payment for Order {uuid.uuid4()}",
                        timestamp=timezone.now(),
                        transaction_type='Debit'
                    )

                    payment = Payment.objects.create(
                        method=payment_method,
                        user=request.user,
                        amount=total_price,
                        status='Completed'
                    )

                    order = Order.objects.create(
                        user=request.user,
                        address=selected_address,
                        payment=payment,
                        order_id=str(uuid.uuid4()),
                        total_price=main_total,
                        offer_price=coupon_discount,
                        final_price=total_price,
                        shipping=shipping_charge,
                        status='Pending'
                    )

                    OrderAddress.objects.create(
                        user=request.user,
                        name=selected_address.name,
                        house_name=selected_address.house_name,
                        street_name=selected_address.street_name,
                        pin_number=selected_address.pin_number,
                        district=selected_address.district,
                        state=selected_address.state,
                        phone_number=selected_address.phone_number
                    )

                    for item in cart_items:
                        item_discount = (item.sub_total() / (total_price + coupon_discount)) * coupon_discount
                        OrderItem.objects.create(
                            order=order,
                            product_variant=item.variant,
                            quantity=item.quantity,
                            price=item.variant.offer_price,
                            coupon_offer=item_discount,
                            paid_price=item.variant.offer_price - item_discount
                        )
                        item.variant.variant_stock -= item.quantity
                        item.variant.save()

                    if applied_coupon_id:
                        UserCoupon.objects.create(
                            user=request.user,
                            coupon=coupon,
                            used=True,
                            used_at=timezone.now(),
                            order=order
                        )

                    cart.items.all().delete()
                    messages.success(request, 'Order placed successfully using Wallet!')
                    return render(request, 'UserSide/order_placed.html', {'order': order})
                else:
                    messages.error(request, 'Insufficient balance in your wallet. Please choose another payment method.')
                    return redirect('checkout')

    return redirect('checkout')


@never_cache
@require_POST
def verify_payment(request):
    if request.method == 'POST':
        order_payment_id = request.POST.get('razorpay_order_id') or request.session.get('razorpay_order_id')
        payment_id = request.POST.get('razorpay_payment_id')
        signature = request.POST.get('razorpay_signature')

        if not all([order_payment_id, payment_id, signature]):
            messages.error(request, 'Missing payment details.')
            return redirect('checkout')

        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

        params_dict = {
            'razorpay_order_id': order_payment_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        print("call back ")

        try:
            # Attempt to verify the Razorpay payment signature
            client.utility.verify_payment_signature(params_dict)
            print(params_dict)
            try:
                # Fetch the order by its order ID
                order = Order.objects.get(order_id=order_payment_id)
            except Order.DoesNotExist:
                messages.error(request, 'Order not found.')
                return render(request, 'UserSide/payment_failed.html')

            # If signature verification is successful, create a successful payment and update the order
            payment = Payment.objects.get(order=order)
            payment.status = 'Completed'
            payment.save()
            
            order.status = 'Shipped'  # Update the order status to 'Shipped'
            order.save()
            

            # Clear the cart after successful payment
            Cart.objects.filter(user=request.user).delete()

            # Show success message
            messages.success(request, 'Payment successful and order confirmed!')
            return render(request, 'UserSide/order_placed.html', {'order': order})

        except razorpay.errors.SignatureVerificationError:
            # If the signature verification fails, handle the failure
            try:
                order = Order.objects.get(order_id=order_payment_id)
                print(order)
                # Create a failed payment record
                payment = Payment.objects.create(
                    method='razorpay',
                    user=order.user,
                    amount=order.final_price,
                    status='Failed'  # Mark the payment as failed
                )

                # Update the order to reflect the payment failure, but keep it as pending
                order.payment = payment
                order.status = 'Pending'  # Keep the order as pending
                order.save()

            except Order.DoesNotExist:
                messages.error(request, 'Order not found during payment failure handling.')
                return render(request, 'UserSide/payment_failed.html')

            # Show error message
            messages.error(request, 'Payment verification failed or was canceled.')
            return render(request, 'UserSide/payment_failed.html')

    # If the request method is not POST or other errors occur
    messages.error(request, 'Invalid request.')
    return render(request, 'UserSide/payment_failed.html')



def calculate_cart_total(user):
    cart_items = CartItem.objects.filter(cart__user=user, is_active=True)
    return sum(item.variant.price * item.quantity for item in cart_items)
   
   
   
@login_required
def my_orders(request):
    orders = Order.objects.filter(user_id=request.user.id).select_related('payment')
    orders_list = orders.exclude(payment__isnull=True).exclude(payment__status__in=[ 'Failed', 'Incomplete'])

    paginator = Paginator(orders_list, 10) 
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    return render(request, 'UserSide/my_orders.html', {'orders': orders})


@user_passes_test(is_admin)
def order_details_admin(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)  
    return render(request, 'AdminSide/order_details.html', {'order': order})

@active_user_required
def order_details_user(request,order_id):
    order = get_object_or_404(Order, order_id=order_id)
   
    return render(request, 'UserSide/order_details.html', {'order': order})



@active_user_required
def cancel_order(request, order_id):
    
    order = get_object_or_404(Order, order_id=order_id)
    

    if order.status == 'Delivered':
        messages.error(request, "Order cannot be canceled.")
        return redirect('order_management:my_orders')

    wallet = None 
    if order.payment.method == 'razorpay':
        if order.payment.status=='Failed':
            messages.error(request, "Complete the payment.")
            return redirect('order_management:my_orders')
    
    if order.payment.method != 'cashOnDelivery':
        wallet, created = Wallet.objects.get_or_create(user=order.user)

    try:
        with transaction.atomic():
            for item in order.items.all():
                product_variant = item.product_variant
                product_variant.variant_stock += item.quantity
                product_variant.save()
                if wallet:
                    wallet.balance += order.final_price-order.shipping
                    wallet.save()

                    WalletTransaction.objects.create(
                        wallet=wallet,
                        amount=item.paid_price,
                        description=f"Refund for item {item.product_variant} in Order {order.order_id} cancellation",
                        transaction_type="Credit"
                    )

            order.status = 'Cancelled'
            order.save()
            

        messages.success(request, "Order canceled successfully and refunds processed.")
    except Exception as e:
        messages.error(request, f"An error occurred while canceling the order: {str(e)}")

    return redirect('order_management:my_orders')

@active_user_required
def return_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    if order.status != 'Delivered':
        messages.error(request, "Only delivered orders can be returned.")
        return redirect('order_management:my_orders')

    existing_return = Return.objects.filter(order=order, user=request.user).first()
    if existing_return:
        messages.error(request, "You have already requested a return for this order.")
        return redirect('order_management:my_orders')

    days_since_delivery = (timezone.now().date() - order.delivered_date).days
    if days_since_delivery > 7:
        messages.error(request, "You can only return an order within 7 days of delivery.")
        return redirect('order_management:my_orders')

    if request.method == 'POST':
        return_reason = request.POST.get('return_reason')
        additional_comments = request.POST.get('additional_comments', '')

        new_return = Return.objects.create(
            order=order,
            user=request.user,
            reason=return_reason,
            status='Pending',
            return_date=timezone.now()
        )

        messages.success(request, "Your return request has been submitted successfully. You will be notified once the admin processes it.")
        return redirect('order_management:my_orders')

    return redirect(reverse('order_management:my_orders'))



@user_passes_test(is_admin)
def change_status(request, order_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            order = get_object_or_404(Order, id=order_id)

            if order.payment.method =='razorpay':
                if order.payment.status=='Failed':
                     messages.error(request, "Customer Failed to Pay.")
                     return JsonResponse({'success': False, 'error': 'Order already cancelled'}, status=400)
                    
            if order.status == 'Cancelled':
                messages.error(request, "Customer already cancelled the item.")
                return JsonResponse({'success': False, 'error': 'Order already cancelled'}, status=400)

            if new_status:
                order.status = new_status

                # Update delivered date and payment status if the order is delivered
                if order.status == "Delivered":
                    order.delivered_date = timezone.now()
                    if order.payment.method == "cashOnDelivery":
                        order.payment.status = "Completed"
                        order.payment.save()

                order.save()
                return JsonResponse({'success': True, 'status': new_status})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
