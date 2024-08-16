from django.shortcuts import redirect, get_object_or_404,redirect ,render 
from django.contrib import messages
from django.http import HttpResponse
from .models import Cart, CartItem, Products, ProductVariant
from django.contrib.auth.decorators import login_required
from products.models import ProductVariantImages
@login_required
def cart_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.filter(is_active=True)

    for item in cart_items:
        item.variant_image = ProductVariantImages.objects.filter(product_variant=item.variant).first()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'UserSide/cart.html', context)

@login_required
def add_cart(request, id):
    product = get_object_or_404(Products, id=id)
    variant_id = request.GET.get('variant_id')
    if not variant_id:
        messages.error(request, 'Select the varient first.')
        return redirect(request.META.get('HTTP_REFERER', '/'))  

    variant = get_object_or_404(ProductVariant, id=variant_id)

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.info(request, 'Item quantity updated in your cart.')
    else:
        messages.success(request, 'Item added to your cart.')

    return redirect(request.META.get('HTTP_REFERER', '/'))


def remove_cart_item(request,id):
    cart_item = get_object_or_404(CartItem, id=id, cart__user=request.user)

    cart_item.delete()
    messages.success(request, 'Item removed from your cart.')

    return redirect(request.META.get('HTTP_REFERER', '/'))
