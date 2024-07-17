from django.shortcuts import render
from django.http import HttpResponse
from catogory.models import Category
def catogory_list(request):
    return render(request,'AdminSide/catogory_list.html')

def add_catogory(request):
    if request.method=='POST':
        catogory_name=request.POST.get('category_name')
        discription=request.POST.get('category_description')
        status=request.POST.get('category_status')
        

    return render(request,'AdminSide/add_catogory.html')


