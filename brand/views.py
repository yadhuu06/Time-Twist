from django.shortcuts import render


# Create your views here.
def Brands_list(request):
    return render(request,'AdminSide/brands_.html')
def add_brand(request,):
    return render(request,'AdminSide/add_brand.html')