from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages


def AdminLogin(request):
    return render(request,'AdminSide/admin_login.html')

def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        

        if user is not None:
            if user.is_admin:
                login(request, user)
                return HttpResponse("welcome admin")
                # return redirect('admin_dashboard') 
            else:
                messages.error(request, 'You are not authorized to access this page.')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'admin_side/admin_login.html')

