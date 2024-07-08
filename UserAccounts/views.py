from django.shortcuts import render, redirect
from django.contrib import messages

import random
from django.core.mail import send_mail
def Register(request):
    if request.method=='POST':
        
        Fname=request.POST.get('firstname')
        Lname=request.POST.get('lastname')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        # pass2=request.POST.get('password2')
        otp = random.randint(1000, 9999)
        
        send_mail(
            'Your OTP Code',
            f'Your OTP code is {otp}',
            'yadhupaikkattu3232@gmail.com',
            [email],
            fail_silently=False,
        )
        print("hai")
        return render(request, 'Otp.html')


    

def signup(request):
    
    return render (request,'Signup.html')

