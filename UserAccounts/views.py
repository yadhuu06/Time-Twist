from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import IntegrityError 
from django.core.mail import send_mail
from .models import User  
from datetime import datetime
from django.contrib import messages
from .forms import RegisterForm
from datetime import datetime, timedelta
import random






def Register(request):
    if request.method == 'POST':
        Fname = request.POST.get('firstname')
        Lname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        pass1 = request.POST.get('password1')
        pass2=request.POST.get('password2')
        if pass1!=pass2:
        
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return render(request, 'Register.html')
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
        return render(request,'Register.html')
    
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<     USER       OTP     VERIFICATION           >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def verify_otp(request):
    if request.method == 'POST':
        enteredOTP = request.POST.get('otp')
        print(enteredOTP)
        otp_generation_time_str = request.session.get('time')
        
        if otp_generation_time_str is None:
            messages.error(request, "Session expired. Please try again.")
            return render(request, 'Otp.html')
        
        otp_generation_time = datetime.strptime(otp_generation_time_str, '%Y-%m-%d %H:%M:%S')
        otp_generation_time = timezone.make_aware(otp_generation_time, timezone.get_current_timezone())
        current_time = timezone.now()
        time_difference = current_time - otp_generation_time
        
        if time_difference <= timedelta(seconds=60):
            validationOnTime = True
        else:
            validationOnTime = False

        if enteredOTP == request.session.get('otp') and validationOnTime:
            Fname = request.session.get('Fname')
            Lname = request.session.get('Lname')
            email = request.session.get('email')
            pass1 = request.session.get('pass1')
            phone = request.session.get('phone')
            User = get_user_model()
            try:
                user = User.objects.create_user(email=email, first_name=Fname, last_name=Lname, phone_number=phone, password=pass1)
                user.is_active = True  
                user.save()

                request.session.clear()

                return render(request, 'Home.html')
            except IntegrityError:  #error handled to work on existing email
                messages.error(request, "This email is already registered. Please use a different email.")
                return render(request, 'Register.html')  
        else:
            if not validationOnTime:
                messages.error(request, "OTP has expired. Please request a new one.")
            else:
                messages.error(request, "Failed to verify OTP. Please try again.")
                
            return render(request, 'Otp.html')

        
def google_login(request):
    return HttpResponse("hai")

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<            USER LOGIN              >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def signup(request):
    
    return render (request,'login.html')

def login(request):
    if request.method == 'POST':
        login_mail = request.POST.get('Email')
        login_password = request.POST.get('Password')
        
        user = authenticate(request, username=login_mail, password=login_password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('home') 
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'login.html')