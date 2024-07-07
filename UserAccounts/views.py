from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm, OtpForm
import random
from django.core.mail import send_mail

def signup(request):
    return render (request,'Signup.html')


def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp_via_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}.'
    from_email = 'your-email@example.com'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def Register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            request.session['registration_data'] = form.cleaned_data
            otp = generate_otp()
            request.session['otp'] = otp
            send_otp_via_email(form.cleaned_data['email'], otp)
            return redirect('otp')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def Otp(request):
    if request.method == "POST":
        form = OtpForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if otp == request.session.get('otp'):
                # OTP is correct, save user data
                data = request.session.get('registration_data')
                # Save the user to the database (e.g., using Django's User model)
                # from django.contrib.auth.models import User
                # user = User.objects.create_user(
                #     username=data['username'],
                #     password=data['password'],
                #     email=data['email']
                # )
                # user.profile.phone = data['phone']
                # user.save()

                # Clear the session data
                del request.session['registration_data']
                del request.session['otp']

                messages.success(request, 'Registration successful.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                return redirect('otp')
    else:
        form = OtpForm()
    return render(request, 'otp.html', {'form': form})

    
    
    
    
    
    
    
    
