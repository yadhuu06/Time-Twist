from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Category, Brand,Products
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Category, Brand, Products, ProductVariant, ProductVariantImages
from catogory.models import Category
from brand.models import Brand
from utils.decorators import admin_required
from django.http import HttpResponse



def products_list(request):
    products=Products.objects.all().order_by('id')
    return render(request,'AdminSide/product_list.html',{"products":products})

def is_admin(user):
    return user.is_authenticated and user.is_staff

@admin_required
def add_products(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_description = request.POST.get('product_description')
        product_category_id = request.POST.get('product_category')
        product_brand_id = request.POST.get('product_brand')
        price = request.POST.get('price')
        offer_price = request.POST.get('offer_price')
        is_active = request.POST.get('is_active') == 'on'

        product_category = Category.objects.get(id=product_category_id) if product_category_id else None
        product_brand = Brand.objects.get(id=product_brand_id) if product_brand_id else None

        if Products.objects.filter(product_name=product_name).exists():
            messages.warning(request, 'Product already exists.')
        else:
            product = Products(
                product_name=product_name,
                product_description=product_description,
                product_category=product_category,
                product_brand=product_brand,
                price=price,
                offer_price=offer_price,
                is_active=is_active,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            product.save()
            messages.success(request, 'Product created successfully.')

        return redirect('products:products_list')  

    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'AdminSide/add_Products.html', {'categories': categories, 'brands': brands})


@admin_required
def add_productVarient(request, Products_id):
    if request.method == "POST":
        # Retrieve form data
        product_id = request.POST.get('product')
        variant_name = request.POST.get('variant_name')
        price = request.POST.get('price')
        variant_stock = request.POST.get('variant_stock')
        colour_code = request.POST.get('colour_code')
        is_active = request.POST.get('is_active') == 'true'
        images = request.FILES.getlist('images')
        
        # Check if the variant already exists for the selected product
        if ProductVariant.objects.filter(product_id=product_id, variant_name=variant_name).exists():
            messages.error(request, 'This product variant already exists.')
            return render(request, 'AdminSide/productVarient.html', {
                'Products_id': Products_id,
                'categories': Category.objects.all(),
                'brands': Brand.objects.all(),
                'products': Products.objects.all(),
                'variant_name': variant_name,
                'price': price,
                'variant_stock': variant_stock,
                'colour_code': colour_code,
                'is_active': is_active,
            })
        
        # Create the new product variant
        product_variant = ProductVariant.objects.create(
            product_id=product_id,
            variant_name=variant_name,
            price=price,
            variant_stock=variant_stock,
            colour_code=colour_code,
            is_active=is_active,
        )

        # Save the uploaded images for the variant
        for image in images:
            ProductVariantImages.objects.create(
                product_variant=product_variant,
                image=image
            )

        messages.success(request, 'Product variant added successfully.')
        return redirect('products:products_list')  
    
    # Load the necessary data for the form
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Products.objects.all()
    return render(request, 'AdminSide/productVarient.html', {
        'Products_id': Products_id,
        'categories': categories,
        'brands': brands,
        'products': products
    })

@admin_required
def edit_productVariant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    
    if request.method == "POST":
        
        variant.variant_name = request.POST.get('variant_name')
        variant.price = request.POST.get('price')
        variant.variant_stock = request.POST.get('variant_stock')
        variant.colour_code = request.POST.get('colour_code')
        variant.is_active = request.POST.get('is_active') == 'true'
        
        images = request.FILES.getlist('images')
        if images:
            
            ProductVariantImages.objects.filter(product_variant=variant).delete()
            for image in images:
                ProductVariantImages.objects.create(
                    product_variant=variant,
                    image=image
                )

        variant.save()
        messages.success(request, 'Product variant updated successfully.')
        return redirect('products:list_productVarient', Products_id=variant.product.id)  # Updated URL name
 
    return render(request, 'AdminSide/editProductVariant.html', {
        'variant': variant
    })

    
@admin_required
def product_detail(request,Products_id):
    products = get_object_or_404(Products, id=Products_id) 
    images = ProductVariantImages.objects.filter(product_variant__product=products)
    variants = ProductVariant.objects.filter(product=products.id)

    return render(request, 'AdminSide/product_details.html', {'products': products, 'images': images , 'variants':variants})

def list_productVarient(request, Products_id):
    # Get the product based on Products_id
    product = get_object_or_404(Products, id=Products_id)
    
    # Get all variants related to the specific product
    variants = ProductVariant.objects.filter(product=product)
    
    context = {
        'product': product,
        'variants': variants,
    }
    
    return render(request, 'AdminSide/varient_list.html', context)


@admin_required
def edit_product(request, product_id):
    product = get_object_or_404(Products, id=product_id) 
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_description = request.POST.get('product_description')
        product_category_id = request.POST.get('product_category')
        product_brand_id = request.POST.get('product_brand')
        price = request.POST.get('price')
        offer_price = request.POST.get('offer_price')
        is_active = request.POST.get('is_active') == 'on'

        product_category = Category.objects.get(id=product_category_id) if product_category_id else None
        product_brand = Brand.objects.get(id=product_brand_id) if product_brand_id else None

        # Update the product fields
        product.product_name = product_name
        product.product_description = product_description
        product.product_category = product_category
        product.product_brand = product_brand
        product.price = price
        product.offer_price = offer_price
        product.is_active = is_active
        product.updated_at = timezone.now()
        product.save()

        messages.success(request, 'Product updated successfully.')
        return redirect('products:products_list')  
    
    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'AdminSide/edit_product.html', {'product': product, 'categories': categories, 'brands': brands})

def shop_view(request):
    if request.user.is_authenticated:
        products = Products.objects.filter(is_active=True).prefetch_related('variants__images')
        
        user_details = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone_number': request.user.phone_number
        }
        
        response = render(request, 'UserSide/shop.html', {'products': products, 'user_details': user_details})
        response['Cache-Control'] = 'no-store'
        return response
    else:   
        return redirect('login')
