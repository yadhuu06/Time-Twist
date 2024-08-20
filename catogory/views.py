from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from catogory.models import Category
from products.models import ProductVariant
from products.models import Products
from django.contrib import messages

def catogory_list(request):
    catogories=Category.objects.all()      
    return render(request,'AdminSide/catogory_list.html',{'catogory':catogories})

def add_catogory(request):
    if request.method == 'POST':
        catogory_name = request.POST.get('category_name').strip()  
        discription = request.POST.get('category_description')
        status = request.POST.get('category_status')

        if not catogory_name:
            messages.error(request, "Category name cannot be empty or whitespace.")
            return render(request, 'AdminSide/add_catogory.html')
        
        if Category.objects.filter(category_name=catogory_name).exists():
            messages.error(request, "A category with this name already exists.")
            return render(request, 'AdminSide/add_catogory.html')
        
        new_catogory = Category(category_name=catogory_name, category_description=discription, is_available=status)
        new_catogory.save()
        messages.success(request, "Category created successfully")
        return redirect('catogory:catogory_list')
        
    return render(request, 'AdminSide/add_catogory.html')


def edit_category(request, category_id):
    category = get_object_or_404(Category, id=catogory_id)
    
    if request.method == 'POST':
        category_name = request.POST.get('category_name').strip()  
        description = request.POST.get('category_description')
        status = request.POST.get('is_available') == 'true'

        if not category_name:  
            messages.error(request, "Category name cannot be empty or whitespace.")
            return render(request, 'AdminSide/edit_category.html', {'category': categories})
        
 
        if Category.objects.filter(catogory_name=category_name).exclude(id=category_id).exists():
            messages.error(request, "A category with this name already exists.")
            return render(request, 'AdminSide/edit_category.html')
        
        category.category_name = category_name
        category.category_description = description
        category.is_available = status
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('category:category_list')

    return render(request, 'AdminSide/edit_category.html', {'category': category})


def varient_list(request):
    varient=ProductVariant.objects.all()
  
    
    return render(request,'AdminSide/varient_list.html',{'varient':varient})