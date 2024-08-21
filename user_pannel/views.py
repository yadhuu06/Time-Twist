from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from .models import UserAddress
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Category, Brand, Products, ProductVariant, ProductVariantImages
from brand.models import Brand
from cart.models import Cart
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import JsonResponse
from cart.models import CartItem
from django.views.decorators.cache import never_cache


@never_cache
@login_required
def add_address(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        house_name = request.POST.get('house_name')
        street_name = request.POST.get('street_name')
        pin_number = request.POST.get('pin_number')
        district = request.POST.get('district')
        state = request.POST.get('state')
        phone_number = request.POST.get('phone_number')

        if UserAddress.objects.filter(user=request.user, house_name=house_name, street_name=street_name, pin_number=pin_number).exists():
            messages.error(request, 'This address already exists.')
            return redirect('user_profile')

        address = UserAddress(
            user=request.user,
            name=name,
            house_name=house_name,
            street_name=street_name,
            pin_number=pin_number,
            district=district,
            state=state,
            phone_number=phone_number,
            status=True,
        )
        address.save()
        messages.success(request, 'Address added successfully!')
        return redirect('user_profile')

    messages.error(request, "Failed to add address.")
    return redirect('user_profile')

@login_required
@never_cache
def edit_address(request, address_id):
    address = get_object_or_404(UserAddress, id=address_id, user=request.user)

    if request.method == 'POST':
        address.name = request.POST.get('name')
        address.house_name = request.POST.get('house_name')
        address.street_name = request.POST.get('street_name')
        address.pin_number = request.POST.get('pin_number')
        address.district = request.POST.get('district')
        address.state = request.POST.get('state')
        address.phone_number = request.POST.get('phone_number')


        if 'set_as_primary' in request.POST:
            UserAddress.objects.filter(user=request.user).update(status=False)
            address.status = True
        address.save()
        messages.success(request, 'Address updated successfully!')
        return redirect('user_profile')

    return render(request, 'edit_address.html', {'address': address})

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(UserAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
        return redirect('user_profile')

    return render(request, 'UserSide/user-login/confirm_delete.html', {'address': address})

@login_required
@never_cache
def user_profile(request):
    current_user = request.user
    addresses = UserAddress.objects.filter(user_id=current_user.id)
     
    context = {
        'user': current_user,
        'addresses': addresses  
    }

    return render(request, 'UserSide/user-login/user_profile.html', context)

@never_cache
@login_required
def shop_view(request):
    if request.user.is_authenticated:
        # Get filter and sort parameters
        category_filter = request.GET.get('category')
        brand_filter = request.GET.get('brand')
        price_sort = request.GET.get('priceSort')
        name_sort = request.GET.get('nameSort')

        # Get the base query set
        products = Products.objects.filter(is_active=True)

        # Apply category filter
        if category_filter:
            products = products.filter(product_category=category_filter)

        # Apply brand filter
        if brand_filter:
            products = products.filter(product_brand=brand_filter)

        # Apply price sort
        if price_sort == 'low-to-high':
            products = products.order_by('offer_price')
        elif price_sort == 'high-to-low':
            products = products.order_by('-offer_price')

        # Apply name sort
        if name_sort == 'aA-zZ':
            products = products.order_by('product_name')
        elif name_sort == 'zZaA':
            products = products.order_by('-product_name')

        # Search functionality
        query = request.GET.get('search_input', '')
        if query:
            products = products.filter(
                Q(product_name__icontains=query) | Q(product_brand__brand_name__icontains=query)
            )

        # Prefetch related objects
        products = products.prefetch_related('variants__images')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            product_html = render_to_string('UserSide/product_list.html', {'products': products})
            return JsonResponse({'product_html': product_html})

        brands = Brand.objects.filter(status=True)
        categories = Category.objects.all()

        user_details = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone_number': request.user.phone_number
        }

        # Render the response
        response = render(request, 'UserSide/shop.html', {
            'products': products,
            'user_details': user_details,
            'brands': brands,
            'categories': categories,
        })
        response['Cache-Control'] = 'no-store'
        return response
    else:
        return redirect('login')
@never_cache     
@login_required
def product_detail_user(request, id):
    try:
        product = Products.objects.get(id=id)
        variants = product.variants.all().prefetch_related('images')
        cart_items = CartItem.objects.filter(cart__user=request.user, product=product)

        variant_data = []
        for variant in variants:
            variant_in_cart = any(cart_item.variant.id == variant.id for cart_item in cart_items)
            variant_data.append({
                'id': variant.id,
                'name': variant.variant_name,
                'price': str(variant.price),
                'colour_code': variant.colour_code,
                'images': [image.image.url for image in variant.images.all()],
                'in_cart': variant_in_cart
            })
    except Products.DoesNotExist:
        product = None
        variant_data = []

    context = {
        'product': product,
        'variants': variant_data
    }
    return render(request, 'UserSide/product_detailss.html', context)


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.filter(is_active=True)
    user_address = UserAddress.objects.filter(user=request.user)
    
    
    out_of_stock = False
    total_price = 0
    for i in cart_items:
        print(i.variant.price)
    
    for item in cart_items:
        if item.quantity > item.variant.variant_stock:
            out_of_stock = True
            messages.error(request, f"Insufficient stock for {item.product.product_name} - {item.variant.variant_name}. Available stock is {item.variant.variant_stock}.")
            

    if out_of_stock:
        return redirect('cart:cart_view')  
    
    for item in cart_items:
        item.variant_image = ProductVariantImages.objects.filter(product_variant=item.variant).first()
        total_price += item.sub_total()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'user_address': user_address,
        'total_price': total_price,
    }
    return render(request, 'UserSide/checkout.html', context)

    
    