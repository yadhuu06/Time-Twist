from django.shortcuts import redirect, get_object_or_404,redirect ,render 
from django.contrib import messages
from django.http import HttpResponse
from .models import Cart, CartItem, Products, ProductVariant
from django.contrib.auth.decorators import login_required
from products.models import ProductVariantImages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from.models import Wishlist,Wallet
import json



@never_cache
@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_items = cart.items.filter(is_active=True)
 
    for item in cart_items:
        item.variant_image = ProductVariantImages.objects.filter(product_variant=item.variant).first()


    cart_total = sum(item.sub_total() for item in cart_items)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total': cart_total, 
    }
    
    return render(request, 'UserSide/cart.html', context)




@login_required
def add_cart(request, id):
    product = get_object_or_404(Products, id=id)
    variant_id = request.GET.get('variant_id')
    
    if not variant_id:
        messages.error(request, 'Select the variant first.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={'quantity': 1}
    )

    if created:

        messages.success(request, 'Item added to your cart.')
    else:
        messages.info(request, 'Item already in your cart.')

    return redirect(request.META.get('HTTP_REFERER', '/'))


def remove_cart_item(request,id):
    cart_item = get_object_or_404(CartItem, id=id, cart__user=request.user)

    cart_item.delete()
    messages.success(request, 'Item removed from your cart.')

    return redirect(request.META.get('HTTP_REFERER', '/'))

@require_POST
def update_cart_quantity(request):
    try:
        data = json.loads(request.body) 
        item_id = data.get('item_id')
        quantity = int(data.get('quantity'))

        cart_item = get_object_or_404(CartItem, id=item_id)
        variant = get_object_or_404(ProductVariant, id=cart_item.variant.id)

        if quantity > variant.variant_stock:
            return JsonResponse({'success': False, 'error': f'Insufficient stock available for {cart_item.product.product_name} - {variant.variant_name}.'})

        cart_item.quantity = quantity
        cart_item.save()

        response_data = {
            'success': True,
            'subtotal': cart_item.sub_total()
        }
        return JsonResponse(response_data)

    except (ValueError, TypeError) as e:
        return JsonResponse({'success': False, 'error': str(e)})
    


def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    wishlist_data = []
    for item in wishlist_items:
        product = item.product
        variant = product.variants.filter(is_active=True).first()
        stock_status = "Out of Stock"
        stock_class = "out-of-stock"

        if variant:
            if variant.variant_stock > 10:
                stock_status = "In Stock"
                stock_class = "in-stock"
            elif 0 < variant.variant_stock <= 10:
                stock_status = "Limited Stock"
                stock_class = "limited-stock"

            image = variant.images.first().image if variant.images.exists() else "static/UserSide/img/No_Images_available.png"
        else:
            image = "static/UserSide/img/No_Images_available.png"

        wishlist_data.append({
            'product': product,
            'variant': variant,
            'stock_status': stock_status,
            'stock_class': stock_class, 
            'image': image,
        })

    return render(request, 'UserSide/wishlist.html', {'wishlist_data': wishlist_data})




def add_to_wishlist(request, product_id):
   
    product = get_object_or_404(Products, id=product_id)
    print('haii')
    
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        messages.info(request, 'This item is already in your wishlist.')
    else:
        messages.success(request, 'Item added to your wishlist.')
    return redirect('shop_view')

def remove_from_wishlist(request, item_id):
    print(item_id) 
   
    item_id=item_id
    wishlist_item = get_object_or_404(Wishlist, product_id=item_id, user=request.user)
    
  
    wishlist_item.delete()
   
    messages.success(request,"item removed from wishlist")
    return redirect('cart:wishlist')

def wallet_detail(request):
    user = request.user
    return render(request,'UserSide/user_wallet.html')