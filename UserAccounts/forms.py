
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from .models import User
from django.contrib.auth import authenticate
import logging




class RegisterForm(forms.Form):
    firstname = forms.CharField(max_length=100, min_length=6, required=True)
    lastname = forms.CharField(max_length=100, min_length=6, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=10, min_length=10, required=True)
    password = forms.CharField(widget=forms.PasswordInput, min_length=6, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=6, required=True)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise ValidationError("Phone number must contain only digits.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise ValidationError("Password and Confirm Password do not match.")
        

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            
            if self.user_cache is None:
                raise ValidationError("Invalid email or password.")
            elif not self.user_cache.is_active:
                raise ValidationError("This account is inactive.")

        return cleaned_data
