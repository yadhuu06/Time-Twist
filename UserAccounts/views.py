from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.templatetags.static import static
from datetime import datetime, timedelta
import random
from .forms import EmailAuthenticationForm, PasswordResetRequestForm
from django.db import IntegrityError
from products.models import Category, Brand, Products, ProductVariant, ProductVariantImages
from django.views.decorators.cache import cache_control
from UserAccounts.models import User
from cart.models import RecentlyViewed
from django.contrib.auth.decorators import login_required
from user_pannel.models import UserAddress
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from django.utils.translation import gettext as _



User = get_user_model()
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< new acount creation view >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def Register(request):
    if request.method == 'POST':
        Fname = request.POST.get('firstname')
        Lname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        
        print("pass1", pass1)
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
        subject = 'Greetings from TimeTwist'
        from_email = 'yadhupaikkattu3232@gmail.com'
        to_email = [email]
        text_content = f'Your Registration OTP Code is {otp}'
        html_content = f'''
            <html>
                <body>
                    <h1>Welcome to Time Twist!</h1>
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
        request.session['time'] = timezone.now().isoformat()

        request.session['Fname'] = Fname
        request.session['Lname'] = Lname
        request.session['email'] = email
        request.session['pass1'] = pass1
        request.session['phone'] = phone

        return render(request, 'UserSide/user-login/otp.html')
    else:
        return render(request, 'UserSide/user-login/register.html')
    
    
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> resend otp <<<<<<<<<<<<<<<<<<<<<<<,


def resend_otp(request):
    otp_generation_time_str = request.session.get('time')
    if otp_generation_time_str:
        otp_generation_time = datetime.strptime(otp_generation_time_str, '%Y-%m-%d %H:%M:%S')
        otp_generation_time = timezone.make_aware(otp_generation_time, timezone.get_current_timezone())
        current_time = timezone.now()
        time_difference = current_time - otp_generation_time

        if time_difference.total_seconds() < 60:
            messages.error(request, 'You can request a new OTP after 1 minute.')
            return render(request, 'UserSide/user-login/otp.html')

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
        messages.success(request, 'OTP has been sent to your email.')
    except Exception as e:
        messages.error(request, 'ERROR occurred sending email. Please try again.')
        return render(request, 'UserSide/user-login/otp.html')
    
    request.session['otp'] = str(otp)
    request.session['time'] = timezone.now().isoformat()


    return render(request, 'UserSide/user-login/otp.html')


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< verify the otp >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.

from django.utils import timezone
from datetime import datetime, timedelta

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_generation_time_str = request.session.get('time')

        if otp_generation_time_str is None:
            messages.error(request, "Session expired. Please try again.")
            return render(request, 'UserSide/user-login/otp.html')

        try:
            otp_generation_time = datetime.fromisoformat(otp_generation_time_str)  # Handles timezone-aware datetime strings
        except ValueError:

            otp_generation_time = datetime.strptime(otp_generation_time_str, '%Y-%m-%d %H:%M:%S')
            otp_generation_time = timezone.make_aware(otp_generation_time, timezone.get_current_timezone())

        current_time = timezone.now()

        
        print(f"Current time: {current_time}")
        print(f"OTP generation time: {otp_generation_time}")

        
        time_difference = current_time - otp_generation_time

       
        if time_difference <= timedelta(seconds=600):
            validation_on_time = True
        else:
            validation_on_time = False

        if entered_otp == request.session.get('otp') and validation_on_time:
            fname = request.session.get('Fname')
            lname = request.session.get('Lname')
            email = request.session.get('email')
            password = request.session.get('pass1')
            
            
            print("password", password)
            

            User = get_user_model()

            try:
               
                user = User.objects.create_user(
                    email=email,
                    first_name=fname,
                    last_name=lname,
                    password =password
                  
                )
                user.is_active = True  
                user.is_blocked = False
                user.save()

                request.session.clear()

                messages.success(request, "Your account has been successfully created. You can now log in.")
                return redirect('login_view')  
            except IntegrityError:
                messages.error(request, "This email is already registered. Please use a different email.")
                return redirect('Register') 
        else:
            if not validation_on_time:
                messages.error(request, "OTP has expired. Please request a new one.")
            else:
                messages.error(request, "Failed to verify OTP. Please try again.")

            return render(request, 'UserSide/user-login/otp.html')
    else:
        return redirect('home_view')



# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Existing user loggin   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>




def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST) 

        if form.is_valid():

            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user =User.objects.get(email=email)
            
            if user.check_password(password):
                print("Password is correct!")
            else:
                print("Password is incorrect.")
                
                
            user = authenticate(username=email, password=password)

            if user is not None:
                if user.is_active and not user.is_blocked:

                    login(request, user)
                    messages.success(request, f"Welcome, {user.first_name} {user.last_name}. You have successfully logged in.")
                    return redirect('home_view')
                else:
                    messages.error(request, "This account is inactive or blocked. Please contact support.")
            else:
                messages.error(request, "Invalid email or password. Please try again.")
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    else:
        form = EmailAuthenticationForm() 

    return render(request, 'UserSide/user-login/login.html', {'form': form})



# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  user loggin success   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>.

@login_required
def home_view(request):
    user=request.user
    if request.user.is_authenticated:
        featured = Products.objects.filter(is_active=True, featured=True)[:4].prefetch_related('variants__images')
        new_launch = Products.objects.filter(is_active=True).order_by('-id')[:5].prefetch_related('variants__images')
        
   
        user_details = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone_number': request.user.phone_number
        }

        response = render(request, 'UserSide/home.html', {

            'featured': featured,
            'new_launch': new_launch,
            'user_details': user_details
        })
        response['Cache-Control'] = 'no-store'
        return response

    else:
        return redirect('Register')

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>. LOG OUT <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def logout_view(request):
    logout(request)
    messages.success(request, "Logout successful")  
    return redirect('login_view')   

def forgot_password(request):
    return render(request,'UserSide/user-login/forgot_password.html')


def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "UserSide/user-login/password_reset_email.html"
                    context = {
                        "email": user.email,
                        "domain": get_current_site(request).domain,
                        "site_name": "Your Site Name",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "https" if request.is_secure() else "http",
                    }
                    email_body = render_to_string(email_template_name, context)
                    send_mail(subject, email_body, "noreply@yourdomain.com", [user.email], fail_silently=False)
                messages.success(request, "A link to reset your password has been sent to your email.")
                return redirect('password_reset_done')
            else:
                messages.error(request, "No registered user found with this email address.")
    else:
        form = PasswordResetForm()

    return render(request, 'UserSide/user-login/password_reset.html', {'form': form})

def password_change_view(request, uidb64, token):
    print(f"uidb64: {uidb64}, token: {token}")
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, user)
                messages.success(request, _('Your password has been reset successfully. You can now log in.'))
                return redirect('login_view')
        else:
            form = SetPasswordForm(user)
        return render(request, 'UserSide/user-login/set_new_password.html', {
            'form': form,
            'uidb64': uidb64,
            'token': token,
        })
    else:
        messages.error(request, _('The reset link is invalid or has expired.'))
        return redirect('password_reset_request')

def password_reset_done(request):
    return render(request, 'UserSide/user-login/password_reset_done.html')