
from .models import Brand
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from utils.decorators import admin_required
import re

def Brands_list(request):
    brands=Brand.objects.all().order_by('id')
    return render(request,'AdminSide/brands_.html',{'brands':brands})

@admin_required
def add_brand(request):
    if request.method == "POST":
        print("its coming")

        brand_name = request.POST.get('brand_name')
        brand_description = request.POST.get('description')
        brand_image = request.FILES.get('brand_image')
        status = request.POST.get('status')
        status = status.lower() == 'true'
        
        if re.fullmatch(r'\s*', brand_name) or re.fullmatch(r'^[^\w\s]*$', brand_name):
            messages.warning(request, 'Brand name cannot be only spaces or special characters.')
            return render(request, 'AdminSide/add_brand.html')

        if Brand.objects.filter(brand_name=brand_name).exists():
            messages.info(request, "Brand already exists.")
            return render(request, 'AdminSide/add_brand.html')

        new_brand = Brand(
            brand_name=brand_name,
            description=brand_description,
            brand_image=brand_image,
            status=status
        )
        new_brand.save()
        messages.success(request, 'Brand created successfully')  
        return redirect('brand:Brands')  
    
    return render(request, 'AdminSide/add_brand.html')

@admin_required
def edit_brand(request, brand_id):
    brand = get_object_or_404(Brand, pk=brand_id)
    print("coming")

    if request.method == "POST":
        print("post")
        new_name = request.POST.get('brand_name')
        new_description = request.POST.get('description')
        new_image = request.FILES.get('brand_image')
        new_status = request.POST.get('status')
        new_status = new_status.lower() == 'true' if new_status else brand.status

        if new_name and (re.fullmatch(r'\s*', new_name) or re.fullmatch(r'^[^\w\s]*$', new_name)):
            messages.warning(request, 'Brand name cannot be only spaces or special characters.')
            return render(request, 'AdminSide/edit_brand.html', {'brand': brand})

        if new_name:
            brand.brand_name = new_name
        if new_description:
            brand.description = new_description
        if new_image:
            brand.brand_image = new_image  
        if new_status is not None:
            brand.status = new_status 
        
        brand.save()
        messages.success(request, 'Changes saved successfully')
        return redirect('brand:Brands') 

    context = {"brand": brand}
    return render(request, 'AdminSide/edit_brand.html', context)
