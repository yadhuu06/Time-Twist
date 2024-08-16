from django.shortcuts import render, redirect, get_object_or_404
from .models import UserAddress
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Category, Brand, Products, ProductVariant, ProductVariantImages
from brand.models import Brand

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

        # Check for duplicate address
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

# def shop_view(request):
#     if request.user.is_authenticated:
#         category_filter = request.GET.get('category')
#         brand_filter = request.GET.get('brand')
#         price_sort = request.GET.get('priceSort')
        

#         products = Products.objects.filter(is_active=True)

#         if category_filter:
#             products = products.filter(product_category=category_filter)
        
#         if brand_filter:
#             products = products.filter(product_brand=brand_filter)
        
#         if price_sort == 'low-to-high':
#             products = products.order_by('price')
#         elif price_sort == 'high-to-low':
#             products = products.order_by('-price')

#         products = products.prefetch_related('variants__images')

#         brands = Brand.objects.filter(status=True)
#         categories = Category.objects.all()

#         user_details = {
#             'first_name': request.user.first_name,
#             'last_name': request.user.last_name,
#             'email': request.user.email,
#             'phone_number': request.user.phone_number
#         }

#         response = render(request, 'UserSide/shop.html', {
#             'products': products, 
#             'user_details': user_details,
#             'brands': brands,
#             'categories': categories,
#         })
#         response['Cache-Control'] = 'no-store'
#         return response
#     else:
#         return redirect('login')



def shop_view(request):
    if request.user.is_authenticated:
        category_filter = request.GET.get('category')
        brand_filter = request.GET.get('brand')
        price_sort = request.GET.get('priceSort')

        products = Products.objects.filter(is_active=True)
     
        if category_filter:
            products = products.filter(product_category=category_filter)
        
        if brand_filter:
            products = products.filter(brand_id=brand_filter)  
        
        if price_sort == 'low-to-high':
            products = products.order_by('price')
        elif price_sort == 'high-to-low':
            products = products.order_by('-price')

        products = products.prefetch_related('variants__images')

        brands = Brand.objects.filter(status=True)
        categories = Category.objects.all()

        user_details = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone_number': request.user.phone_number
        }

        # Render the template with the context data
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
@login_required
def product_detail_user(request, id):
    try:
        product = Products.objects.get(id=id)
        variants = product.variants.all().prefetch_related('images')
        variant_data = []
        for variant in variants:
            variant_data.append({
                'id': variant.id,
                'name': variant.variant_name,
                'price': str(variant.price),  
                'colour_code': variant.colour_code,
                'images': [image.image.url for image in variant.images.all()]
            })
    except Products.DoesNotExist:
        product = None
        variant_data = []

    context = {
        'product': product,
        'variants': variant_data
    }
    return render(request, 'UserSide/product_detailss.html', context)

# def forgot_password(request):    
#     if request.method=='post':
#         email=request.get('email')
#         print(email)
#     return render(request,'UserSide/password_reset.html')

@login_required
def user_profile(request):
    current_user = request.user
    addresses = UserAddress.objects.filter(user_id=current_user.id)
     
    context = {
        'user': current_user,
        'addresses': addresses  
    }

    return render(request, 'UserSide/user-login/user_profile.html', context)





