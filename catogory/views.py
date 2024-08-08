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
    if request.method=='POST':
        catogory_name=request.POST.get('category_name')
        discription=request.POST.get('category_description')
        status=request.POST.get('category_status')
        new_catogory=Category(category_name=catogory_name,category_description=discription,is_available=status)    
        new_catogory.save()
        print ("success")
        messages.success(request,"brand created succesfullly")
        return redirect('catogory:catogory_list')       
        
    return render(request,'AdminSide/add_catogory.html')


def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.category_name = request.POST.get('category_name')
        category.category_description = request.POST.get('category_description')
        category.is_available = request.POST.get('is_available') == 'true'     
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('catogory:catogory_list')  
    
    return render(request, 'AdminSide/edit_catogory.html', {'category': category})
def varient_list(request):
    varient=ProductVariant.objects.all()
  
    
    return render(request,'AdminSide/varient_list.html',{'varient':varient})