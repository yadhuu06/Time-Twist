from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from UserAccounts.models import User
from django.shortcuts import get_object_or_404
from order_management.models import Order, Payment, OrderItem 
from user_pannel.models import UserAddress
from products.models import Products,ProductVariant
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache


def is_admin(user):
    return  user.is_admin


@user_passes_test(is_admin)
@never_cache
def admin_page(request):
    return render(request,'AdminSide/admin-dashboard.html')
    



def admin_login(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)       
        if user is not None:    
            if user.is_admin:
             
                login(request, user)
                return render(request,'AdminSide/admin-dashboard.html')              
            else:
                messages.error(request, 'You are not authorized to access this page.')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'AdminSide/admin_login.html')



@user_passes_test(is_admin)
def users_list(request):
     users = User.objects.filter(is_admin=False) 
     return render(request, 'AdminSide/user_list.html', {'users': users})
    
   
    
@user_passes_test(is_admin)    
def documentaion(request):
    return render(request,'AdminSide/documentation.html')


@never_cache
@user_passes_test(is_admin)
def Block_user(request):
    blocking_mail = request.POST.get('email')
    user = get_object_or_404(User, email=blocking_mail)

    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True

    user.save()
    return redirect('users_list')

def admin_order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'AdminSide/admin_order_list.html', {'orders': orders})

@user_passes_test(lambda user: user.is_superuser)
def change_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        status = request.POST.get('status')
        if status in ['Pending', 'Delivered', 'Accepted', 'Rejected']:
            order.status = status
            order.save()
        return redirect('admin_order_list')