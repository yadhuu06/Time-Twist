from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cart.models import Cart
from user_pannel.models import UserAddress
from products.models import ProductVariant
from order_management.models import Order, Payment, OrderItem 

@login_required
def place_order(request):
    if request.method == 'POST':
        payment_method = request.POST.get('paymentMethod')
        address_id = request.POST.get('address')

        if payment_method == 'cashOnDelivery':
            total_price = calculate_cart_total(request.user)
            if total_price >= 10000:
                messages.error(request, 'Cash on Delivery is not available for orders over Rs 10,000.')
                return redirect('checkout')

        try:
            selected_address = UserAddress.objects.get(id=address_id, user=request.user)
        except UserAddress.DoesNotExist:
            messages.error(request, 'Selected address is invalid.')
            return redirect('checkout')

        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('checkout')

        for item in cart_items:
            product_variant = ProductVariant.objects.get(id=item.variant.id)
            if not product_variant.is_active:
                messages.error(request, f'Product {product_variant.product_name} is no longer available.')
                return redirect('checkout')
            if product_variant.stock < item.quantity:
                messages.error(request, f'Insufficient stock for {product_variant.product_name}.')
                return redirect('checkout')

        payment = Payment.objects.create(method=payment_method, user=request.user, amount=total_price)

        order = Order.objects.create(
            user=request.user,
            address=selected_address,
            payment=payment,
            total_price=total_price
        )

        for item in cart_items:
            product_variant = item.variant
            OrderItem.objects.create(
                order=order,
                product_variant=product_variant,
                quantity=item.quantity,
                price=item.variant.price
            )
            product_variant.stock -= item.quantity
            product_variant.save()
            item.delete()  

        messages.success(request, 'Your order has been placed successfully!')
        return redirect('order_success', order_id=order.id)

    return redirect('checkout')
