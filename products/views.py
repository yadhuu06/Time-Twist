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
from django.core.exceptions import ValidationError
from django.db import transaction
import re
from decimal import Decimal
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Products

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required





@admin_required
def products_list(request):
    query = request.GET.get('q'," ")  # Get the search query from the request
    products_list = Products.objects.all().order_by('id')
    print(query)

    # Search functionality
    if query:
        # Use Q objects to filter products where the name or brand starts with, ends with, or contains the query.
        products_list = products_list.filter(
            Q(product_name__icontains=query) |  # Contains anywhere
            Q(product_name__startswith=query) |  # Starts with
            Q(product_name__endswith=query) |  # Ends with
            Q(product_brand__brand_name__icontains=query) |  # Brand contains
            Q(product_brand__brand_name__startswith=query) |  # Brand starts with
            Q(product_brand__brand_name__endswith=query)  # Brand ends with
        )

    # Pagination
    paginator = Paginator(products_list, 6)  # Show 6 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    return render(request, 'AdminSide/product_list.html', {"products": products, "query": query})


def is_valid_product_name(name):
    if not name.strip():
        return False
    if re.search(r'[^\w\s]', name):
        return False
    return True




@never_cache
@admin_required
def add_products(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name').strip()
        product_description = request.POST.get('product_description').strip()
        product_category_id = request.POST.get('product_category')
        product_brand_id = request.POST.get('product_brand')
        price = request.POST.get('price')
        offer_percentage = request.POST.get('offer_percentage')
        is_active = request.POST.get('is_active') == 'on'

        product_category = Category.objects.get(id=product_category_id) if product_category_id else None
        product_brand = Brand.objects.get(id=product_brand_id) if product_brand_id else None

        if not is_valid_product_name(product_name):
            messages.error(request, 'Product name cannot be empty, contain only spaces, or contain special characters.')
            return render_form(request, product_name, product_description, price, offer_percentage, is_active)

        try:
            price = float(price)
            if price < 100:
                raise ValidationError('Price must be at least 100.')
        except (ValueError, ValidationError) as e:
            messages.error(request, str(e))
            return render_form(request, product_name, product_description, price, offer_percentage, is_active)

        if offer_percentage:
            try:
                offer_percentage = float(offer_percentage)
                if not (0 <= offer_percentage <= 80):
                    raise ValidationError("Offer percentage must be between 0 and 80.")
            except (ValueError, ValidationError) as e:
                messages.error(request, str(e))
                return render_form(request, product_name, product_description, price, offer_percentage, is_active)
        else:
            offer_percentage = 0

        offer_price = price - (price * offer_percentage / 100)

        if Products.objects.filter(product_name=product_name).exists():
            messages.warning(request, 'Product with this name already exists.')
            return render_form(request, product_name, product_description, price, offer_percentage, is_active)

        product = Products(
            product_name=product_name,
            product_description=product_description,
            product_category=product_category,
            product_brand=product_brand,
            price=price,
            offer_percentage=offer_percentage,
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

def render_form(request, product_name='', product_description='', price='', offer_percentage='', is_active=False):
    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'AdminSide/add_Products.html', {
        'categories': categories,
        'brands': brands,
        'product_name': product_name,
        'product_description': product_description,
        'price': price,
        'offer_percentage': offer_percentage,
        'is_active': is_active,
    })


    


@never_cache
@admin_required
def edit_product(request, product_id):
    
    product = get_object_or_404(Products, id=product_id)
    
    if request.method == 'POST':
        product_name = request.POST.get('product_name').strip()
        product_description = request.POST.get('product_description').strip()
        product_category_id = request.POST.get('product_category')
        product_brand_id = request.POST.get('product_brand')
        price = request.POST.get('price')
        offer_percentage = request.POST.get('offer_percentage')
        is_active = request.POST.get('is_active') == 'on'
        featured = request.POST.get('featured') == 'True'
        print(featured)
        print(is_active)
       

     
        if re.match(r'^[^\w]+$', product_name) or not product_name:
            messages.error(request, 'Product name cannot be empty, contain only spaces, or contain special characters.')
            return render(request, 'AdminSide/edit_product.html', {
                'product': product,
                'categories': Category.objects.all(),
                'brands': Brand.objects.all()
            })

        try:
            price = float(price)
            if price < 100:
                raise ValidationError('Price must be at least 100.')
        except (ValueError, ValidationError) as e:
            messages.error(request, str(e))
            return render(request, 'AdminSide/edit_product.html', {
                'product': product,
                'categories': Category.objects.all(),
                'brands': Brand.objects.all()
            })
        if offer_percentage:
            print("in")
            try:
                offer_percentage = float(offer_percentage)
                if not (0 <= offer_percentage <= 80):
                    raise ValidationError('Offer percentage must be between 0 and 80.')
                offer_percentage_decimal = Decimal(offer_percentage) 
            except (ValueError, ValidationError) as e:
                messages.error(request, str(e))
                return render(request, 'AdminSide/edit_product.html', {
                    'product': product,
                    'categories': Category.objects.all(),
                    'brands': Brand.objects.all()
                })
        else:
            offer_percentage_decimal = Decimal('0') 

        product_category = Category.objects.get(id=product_category_id) if product_category_id else None
        product_brand = Brand.objects.get(id=product_brand_id) if product_brand_id else None

       
        product.product_name = product_name
        product.product_description = product_description
        product.product_category = product_category
        product.product_brand = product_brand
        product.price = Decimal(price)  
        product.offer_percentage = offer_percentage_decimal
        product.offer_price= price - (price * offer_percentage / 100)
        product.is_active = is_active
        product.featured = featured
        product.updated_at = timezone.now()
        product.save()

        for variant in product.variants.all():
            variant.offer_price = variant.price - (variant.price * offer_percentage_decimal / Decimal('100'))
            variant.save()

        messages.success(request, 'Product updated successfully.')
        return redirect('products:products_list')
    
    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'AdminSide/edit_product.html', {
        'product': product,
        'categories': categories,
        'brands': brands
    })
    
@never_cache  
@admin_required
def add_productVarient(request, Products_id):
    if request.method == "POST":
        variant_name = request.POST.get('variant_name', '').strip()
        price = request.POST.get('price')
        variant_stock = request.POST.get('variant_stock')
        colour_code = request.POST.get('colour_code')
        is_active = request.POST.get('is_active') == 'true'
        images = request.FILES.getlist('images')

        try:
            product = Products.objects.get(id=Products_id)
        except Products.DoesNotExist:
            messages.error(request, 'Product not found.')
            return redirect('products:products_list')

        if not variant_name:
            messages.error(request, 'Variant name cannot be empty or just spaces.')
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

        try:
            price = Decimal(price)
            if price < Decimal('100'):
                raise ValidationError('Price must be at least 100.')
        except (ValueError, ValidationError) as e:
            messages.error(request, str(e))
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

        try:
            variant_stock = int(variant_stock)
            if variant_stock < 0:
                raise ValidationError('Stock must be a non-negative integer.')
        except (ValueError, ValidationError) as e:
            messages.error(request, str(e))
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

        if not colour_code:
            messages.error(request, 'Colour code cannot be empty.')
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

        if ProductVariant.objects.filter(product=product, variant_name=variant_name).exists():
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

        offer_price = price - (price * Decimal(product.offer_percentage) / Decimal(100))

        try:
            with transaction.atomic():
                product_variant = ProductVariant.objects.create(
                    product=product,
                    variant_name=variant_name,
                    price=price,
                    offer_price=offer_price,
                    variant_stock=variant_stock,
                    colour_code=colour_code,
                    is_active=is_active,
                )

                for image in images:
                    ProductVariantImages.objects.create(
                        product_variant=product_variant,
                        image=image
                    )

            messages.success(request, 'Product variant added successfully.')
            return redirect('products:products_list')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
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

    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Products.objects.all()
    return render(request, 'AdminSide/productVarient.html', {
        'Products_id': Products_id,
        'categories': categories,
        'brands': brands,
        'products': products
    })

    
    
@never_cache     
@admin_required
def edit_productVariant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    
    if request.method == "POST":
        variant_name = request.POST.get('variant_name', '').strip()
        price = request.POST.get('price')
        variant_stock = request.POST.get('variant_stock')
        colour_code = request.POST.get('colour_code')
        is_active = request.POST.get('is_active') == 'true'
        images = request.FILES.getlist('images')

        if not variant_name:
            messages.error(request, 'Variant name cannot be empty or just spaces.')
            return render(request, 'AdminSide/editProductVariant.html', {'variant': variant})

        try:
            price = Decimal(price)
            if price < Decimal('100'):
                raise ValueError('Price must be at least 100.')
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'AdminSide/editProductVariant.html', {'variant': variant})

        try:
            variant_stock = int(variant_stock)
            if variant_stock < 0:
                raise ValueError('Stock must be a non-negative integer.')
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'AdminSide/editProductVariant.html', {'variant': variant})

        if not colour_code:
            messages.error(request, 'Colour code cannot be empty.')
            return render(request, 'AdminSide/editProductVariant.html', {'variant': variant})

        variant.variant_name = variant_name
        variant.variant_stock = variant_stock
        variant.colour_code = colour_code
        variant.is_active = is_active
        variant.price = price
        variant.offer_price = price - (price * Decimal(variant.product.offer_percentage) / Decimal(100))

        if images:
            ProductVariantImages.objects.filter(product_variant=variant).delete()
            for image in images:
                ProductVariantImages.objects.create(product_variant=variant, image=image)

        variant.save()

        messages.success(request, 'Product variant updated successfully.')
        return redirect('products:list_productVarient', Products_id=variant.product.id)

    return render(request, 'AdminSide/editProductVariant.html', {'variant': variant})


@never_cache
@admin_required
def product_detail(request, id):
    products = get_object_or_404(Products, id=id)
    images = ProductVariantImages.objects.filter(product_variant__product=products)
    variants = ProductVariant.objects.filter(product=products.id)
    return render(request, 'AdminSide/product_details.html', {'products': products, 'images': images, 'variants': variants})


@admin_required
def list_productVarient(request, Products_id):
    product = get_object_or_404(Products, id=Products_id)
    variants = ProductVariant.objects.filter(product=product)
    
    context = {
        'product': product,
        'variants': variants,
    }
    return render(request, 'AdminSide/varient_list.html', context)



@login_required
@require_POST
def submit_product_rating(request):
    product_id = request.POST.get('product_id')
    rating = request.POST.get('rating')
    review = request.POST.get('review', '')

    if not product_id or not rating:
        return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)

    try:
        product = Products.objects.get(id=product_id)
        rating_obj, created = ProductRating.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={'rating': rating, 'review': review}
        )
        return JsonResponse({'success': True, 'message': 'Rating submitted successfully'})
    except Products.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


