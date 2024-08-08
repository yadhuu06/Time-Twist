from django.shortcuts import render, HttpResponse, redirect,get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login ,logout
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.templatetags.static import static
from datetime import datetime, timedelta
import random
from .forms import EmailAuthenticationForm 
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from products.models import Category, Brand, Products, ProductVariant, ProductVariantImages
from django.views.decorators.cache import cache_control




User = get_user_model()

def Register(request):
    if request.method == 'POST':
        Fname = request.POST.get('firstname')
        Lname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        if pass1 != pass2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'UserSide/user-login/register.html')
        User = get_user_model()

        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return render(request, 'UserSide/user-login/register.html')

        otp = random.randint(100000, 999999)
        print(otp)        
        image_url = static('UserSide/img/mymail.jpeg')
        subject = 'Greetings from GlowGear'
        from_email = 'yadhupaikkattu3232@gmail.com'
        to_email = [email]
        text_content = f'Your Registration OTP Code is {otp}'
        html_content = f'''
            <html>
                <body>
                    <h1>Welcome to GlowGear!</h1>
                    <h5>The Right Time TO Purchase</h5>
                    <h4>Your Registration OTP Code is: <strong>{otp}</strong></h4>
                    <h4>Thank You For Choosing Us</h4>
                    
                    <img src="{image_url}" alt="Company Logo"; >
                </body>
            </html>
        '''      
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        messages.success(request, 'OTP has been sent to your email. Please verify to complete registration.')
        request.session['otp'] = str(otp)
        request.session['time'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        request.session['Fname'] = Fname
        request.session['Lname'] = Lname
        request.session['email'] = email
        request.session['pass1'] = pass1
        request.session['phone'] = phone

        return render(request, 'UserSide/user-login/otp.html')
    else:
        return render(request, 'UserSide/user-login/register.html')

def resend_otp(request):
    otp_generation_time_str = request.session.get('time')

    #
    otp_generation_time = datetime.strptime(otp_generation_time_str, '%Y-%m-%d %H:%M:%S')
    current_time = timezone.now()

    time_difference = current_time - timezone.make_aware(otp_generation_time)
    if time_difference.total_seconds() < 60:
        messages.error(request, 'You can request a new OTP after 1 minute.')
        return render(request, 'UserSide/otp.html')

    # Generate a new OTP and update the session
    otp = random.randint(100000, 999999)
    print(otp)
    image_url = static('UserSide/img/mymail.jpeg')
    subject = 'Greetings from GlowGear - Resend OTP'
    from_email = 'yadhupaikkattu3232@gmail.com'
    to_email = [request.session.get('email')]
    text_content = f'Your new OTP Code is {otp}'
    html_content = f'''
        <html>
            <body>
                <h1>Welcome to GlowGear!</h1>
                <h5>The Right Time TO Purchase</h5>
                <h4>Your new OTP Code is: <strong>{otp}</strong></h4>
                <h4>Thank You For Choosing Us</h4>
                
                <img src="{image_url}" alt="Company Logo">
            </body>
        </html>
    '''
    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        messages.success(request, ' OTP sent to your email.')
    except Exception as e:
        messages.error(request, 'ERROR occured sending email. Please try again.')
        return render(request, 'UserSide/otp.html')
    request.session['otp'] = str(otp)
    request.session['time'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

    return render(request, 'UserSide/parent/user-login/otp.html')

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_generation_time_str = request.session.get('time')

        if otp_generation_time_str is None:
            messages.error(request, "Session expired. Please try again.")
            return render(request, 'UserSide/parent/otp.html')
        
        otp_generation_time = datetime.strptime(otp_generation_time_str, '%Y-%m-%d %H:%M:%S')
        otp_generation_time = timezone.make_aware(otp_generation_time, timezone.get_current_timezone())
        current_time = timezone.now()
        time_difference = current_time - otp_generation_time

        if time_difference <= timedelta(seconds=60):
            validation_on_time = True
        else:
            validation_on_time = False

        if entered_otp == request.session.get('otp') and validation_on_time:
            fname = request.session.get('Fname')
            lname = request.session.get('Lname')
            email = request.session.get('email')
            password = request.session.get('pass1')
            phone = request.session.get('phone')

            User = get_user_model()

            try:
                user = User.objects.create_user(email=email, first_name=fname, last_name=lname, phone_number=phone, password=password)
                user.is_active = True
                user.save()

                request.session.clear()

                messages.success(request, "Your account has been successfully created. You can now log in.")
                return redirect('login_view')  
            except IntegrityError:
                messages.error(request, "This email is already registered. Please use a different email.")
                return redirect('register') 
        else:
            if not validation_on_time:
                messages.error(request, "OTP has expired. Please request a new one.")
            else:
                messages.error(request, "Failed to verify OTP. Please try again.")

            return render(request, 'UserSide/user-loginotp.html')
    else:
        return redirect('home_view')


def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_active and not user.is_blocked:  
                login(request, user)
                messages.success(request, f"Welcome, {user.email}! You have successfully logged in.")
                return redirect('home_view')
            else:
                messages.error(request, "This account is inactive. Please contact support.")
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    else:
        form = EmailAuthenticationForm()
    return render(request, 'UserSide/user-login/login.html', {'form': form})

def home_view(request):
    if request.user.is_authenticated:
        products = Products.objects.filter(is_active=True).prefetch_related('variants__images')
        response = render(request, 'UserSide/home.html', {'products': products})
        response['Cache-Control'] = 'no-store'
        return response
    
    else:
        # Redirect to login page or handle unauthorized access
        return redirect('Register')  # 
def product_detail_user(request, id):
    try:
        product = Products.objects.get(id=id)
    except Products.DoesNotExist:
        product = None  # Handle this case appropriately
    return render(request, 'UserSide/product_detailss.html', {'product': product})

def forgot_password(request):
    
    if request.method=='post':
        email=request.get('email')
        print(email)
    return render(request,'UserSide/password_reset.html')

def demo(request):
    products = Products.objects.filter(is_active=True).prefetch_related('variants__images')
    response = render(request, 'UserSide/index.html', {'products': products})
    response['Cache-Control'] = 'no-store'
    return response

    