from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from UserAccounts.models import User


def admin_page(request):
    return render(request,'AdminSide/admin-dashboard.html')
    
#    return render(request, 'AdminSide/admin_login.html')

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


def users_list(request):
     user = User.objects.all() 
     
     for i in user:
         print(i) 
     return render(request, 'AdminSide/user_list.html', {'user': user})
    
    
