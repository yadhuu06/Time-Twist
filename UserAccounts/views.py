from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import get_user_model
from django.utils import timezone
import random
from django.core.mail import send_mail
from .models import User  # Import your User model here

def Register(request):
    if request.method == 'POST':
        Fname = request.POST.get('firstname')
        Lname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        pass1 = request.POST.get('password1')
        # pass2=request.POST.get('password2')
        otp = random.randint(1000, 9999)
        
        send_mail(
            'Greetings from GlowGear  ',
            f'Your Registeration OTP Code is {otp}',
            'yadhupaikkattu3232@gmail.com',
            [email],
            fail_silently=False,
        )
        print(otp)
        request.session['otp'] = str(otp)
        
        # Save user details in session for verification
        request.session['Fname'] = Fname
        request.session['Lname'] = Lname
        request.session['email'] = email
        request.session['pass1'] = pass1
        request.session['phone']= phone
        
        return render(request, 'Otp.html')
def verify_otp(request):
    if request.method == 'POST':
        enteredOTP = request.POST.get('otp')
        print(enteredOTP)
        
        if enteredOTP == request.session.get('otp'):
         
            Fname = request.session.get('Fname')
            Lname = request.session.get('Lname')
            email = request.session.get('email')
            pass1 = request.session.get('pass1')
            phone = request.session.get('phone')
            # Create user with UserManager
            User = get_user_model()
            user = User.objects.create_user(email=email, first_name=Fname, last_name=Lname, phone_number=phone, password=pass1)
            user.is_active = True  # Activate user upon successful OTP verification
            user.save()
            
            request.session.clear() # Clear session data after successful registration
            
            return HttpResponse("User created successfully!")
        else:
            return HttpResponse("Failed to verify OTP. Please try again.")

def signup(request):
    
    return render (request,'Signup.html')

