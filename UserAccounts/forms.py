
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from .models import User
from django.contrib.auth import authenticate
import logging




# class RegisterForm(forms.Form):
#     firstname = forms.CharField(max_length=100, min_length=6, required=True)
#     lastname = forms.CharField(max_length=100, min_length=6, required=True)
#     email = forms.EmailField(required=True)
#     phone = forms.CharField(max_length=10, min_length=10, required=True)
#     password = forms.CharField(widget=forms.PasswordInput, min_length=6, required=True)
#     confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=6, required=True)

#     def clean_phone(self):
#         phone = self.cleaned_data.get('phone')
#         if not phone.isdigit():
#             raise ValidationError("Phone number must contain only digits.")
#         return phone

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if User.objects.filter(email=email).exists():
#             raise ValidationError("Email is already registered.")
#         return email

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")

#         # Check if both passwords match
#         if password and confirm_password and password != confirm_password:
#             raise ValidationError("Password and Confirm Password do not match.")

#         return cleaned_data
        

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        label="Email"
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Attempt to authenticate the user
            self.user_cache = authenticate(self.request, username=username, password=password)

            if self.user_cache is None:
                raise ValidationError("Invalid email or password.")
            elif not self.user_cache.is_active:
                raise ValidationError("This account is inactive or blocked. Please contact support.")
        else:
            raise ValidationError("Both email and password are required.")

        return cleaned_data



    
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No registered user found with this email address.")
        return email

class SetPasswordForm(forms.Form):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm New Password"
    )

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        # Add more validation logic if necessary
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return password2