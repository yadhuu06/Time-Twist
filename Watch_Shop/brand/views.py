
from .models import Brand
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .models import Brand



def Brands_list(request):
    brands=Brand.objects.all().order_by('id')
    return render(request,'AdminSide/brands_.html',{'brands':brands})

def add_brand(request):
    if request.method == "POST":
        brand_name = request.POST.get('brand_name')
        brand_description = request.POST.get('description')
        brand_image = request.FILES.get('brand_image')
        status = request.POST.get('status')
        status = status.lower() == 'true'
              
        def check_exist_or_not(brand_name):
            return Brand.objects.filter(brand_name=brand_name).exists()

        
        if check_exist_or_not(brand_name):
            messages.info(request, "Brand already exists.")
            return render(request, 'AdminSide/add_brand.html')
        else:
            
            new_brand = Brand(
                brand_name=brand_name,
                description=brand_description,
                brand_image=brand_image,
                status=status
            )
            new_brand.save()
            messages.success(request, 'Brand created successfully')  
            return redirect('brand:Brands_list')  
    
    return render(request, 'AdminSide/add_brand.html')


def  edit_brand(request, brand_id):
    
    if request.method == "POST":
        brand_id = request.POST.get('brand_id')
        brand = get_object_or_404(Brand, pk=brand_id)
        new_name = request.POST.get('brand_name')
        new_description = request.POST.get('description')
        new_image = request.FILES.get('brand_image')
        new_status = request.POST.get('status')
        if new_name:
            brand.brand_name = new_name
        if new_description:
            brand.description = new_description
        if new_image:
            brand.brand_image = new_image  
            brand.status = new_status 
        
        brand.save()
        messages.success(request, 'Changes saved successfully')
        return redirect('brand:Brands') 
    

    return render(request, 'AdminSide/edit_brand.html')
    