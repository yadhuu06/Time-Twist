from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import get_user_model
from django.utils import timezone
import random
from django.core.mail import send_mail
from .models import User  # Import your User model here
import json
from datetime import datetime
from django.contrib import messages
def Register(request):
    if request.method == 'POST':
        Fname = request.POST.get('firstname')
        Lname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        pass1 = request.POST.get('password1')
        # pass2=request.POST.get('password2')
        otp = random.randint(100000, 999999)
        
        
        send_mail(
            'Greetings from GlowGear  ',
            f'Your Registeration OTP Code is {otp}',
            'yadhupaikkattu3232@gmail.com',
            [email],
            fail_silently=False,
        )
        messages.success(request, 'OTP has been sent to your email. Please verify to complete registration.')
        print(otp)
        request.session['otp'] = str(otp)
        request.session['time'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        request.session['Fname'] = Fname
        request.session['Lname'] = Lname
        request.session['email'] = email
        request.session['pass1'] = pass1
        request.session['phone']= phone
        
        return render(request, 'Otp.html')
    else :
        return render(request,'signup.html')
    
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<     USER       OTP     VERIFICATION           >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def verify_otp(request):
    if request.method == 'POST':
        enteredOTP = request.POST.get('otp')
        print(enteredOTP)
        
        now= datetime.strptime(session_time_str, '%Y-%m-%d %H:%M:%S')
        if now <=request.session.get('time'):
            validationOnTime=True
        
        if enteredOTP == request.session.get('otp') and validationOnTime==True:
         
            Fname = request.session.get('Fname')
            Lname = request.session.get('Lname')
            email = request.session.get('email')
            pass1 = request.session.get('pass1')
            phone = request.session.get('phone')
            # Create user with UserManager
            User = get_user_model()
            user = User.objects.create_user(email=email, first_name=Fname, last_name=Lname, phone_number=phone, password=pass1)
            user.is_active = True  
            user.save()
            
            request.session.clear() 
            
            return render(request,'Home.html')
        else:
            return HttpResponse("Failed to verify OTP. Please try again.")


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<              USER LOGIN              >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def signup(request):
    
    return render (request,'login.html')

def login(request):
    if request.method == 'POST':
        login_mail = request.POST.get('Email')
        login_password = request.POST.get('Password')
        
        user = authenticate(request, username=login_mail, password=login_password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect page
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'login.html')