from django.shortcuts import render, get_object_or_404,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from user_pannel.models import UserAddress
from products.models import ProductVariant
from order_management.models import Order, Payment, OrderItem 
from django.http import HttpResponse
import uuid
from django.views.decorators.http import require_POST
from django.db import transaction




@login_required
def place_order(request):
    if request.method == 'POST':
        payment_method = request.POST.get('paymentMethod')
        address_id = request.POST.get('address')

        if not payment_method or not address_id:
            messages.error(request, 'Please select both a payment method and a delivery address.')
            return redirect('checkout')

        total_price = calculate_cart_total(request.user)

        if payment_method == 'cashOnDelivery':
            if total_price >= 15000:
                messages.error(request, 'Cash on Delivery is not available for orders over Rs 15,000.')
                return redirect('checkout')

        try:
            selected_address = UserAddress.objects.get(id=address_id, user=request.user)
        except UserAddress.DoesNotExist:
            messages.error(request, 'Selected address is invalid.')
            return redirect('checkout')

        cart_items = CartItem.objects.filter(cart__user=request.user, is_active=True)
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

        payment = Payment.objects.create(method=payment_method, user=request.user, amount=total_price)
        order_id = str(uuid.uuid4())
        order = Order.objects.create(
            user=request.user,
            address=selected_address,
            order_id=order_id,
            payment=payment,
            total_price=total_price
        )

        for item in cart_items:
            product_variant = item.variant
            OrderItem.objects.create(
                order=order,
                product_variant=product_variant,
                quantity=item.quantity,
                price=product_variant.offer_price
            )
            product_variant.variant_stock -= item.quantity
            product_variant.save()
            item.delete()  

        messages.success(request, 'Order placed successfully!')
        
        return render(request,'UserSide/order_placed.html',{'order':order})

    return redirect('checkout')

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