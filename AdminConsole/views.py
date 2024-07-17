from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from UserAccounts.models import User
from django.shortcuts import get_object_or_404

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
     users = User.objects.all() 
     
    
     return render(request, 'AdminSide/user_list.html', {'users': users})
    
    
def documentaion(request):
    return render(request,'AdminSide/documentation.html')



def Block_user(request):
    blocking_mail = request.POST.get('email')
    user = get_object_or_404(User, email=blocking_mail)

    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True

    user.save()
    return redirect('users_list')
        