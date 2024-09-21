from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Category, Brand,Products
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Category, Brand, Products

def products_list(request):
    products=Products.objects.all().order_by('id')
    return render(request,'AdminSide/product_list.html',{"products":products})

def is_admin(user):
    return user.is_authenticated and user.is_staff

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
def add_productVarient(request):
    return render(request,'add_productVarient.html')