from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

def save_user_details(backend, user, response, request, *args, **kwargs):
    if backend.name == 'google-oauth2':
        email = response.get('email')
        first_name = response.get('given_name')
        last_name = response.get('family_name')
        
        if not user:
            try:
                # Try to get the user by email
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # If the user doesn't exist, create a new one
                user = User(email=email, first_name=first_name, last_name=last_name)
                user.is_active = True  # You can set default active status here if needed
                user.save()

        # Update the user's details if needed
        if not user.first_name or not user.last_name:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        # Check if the user is active
        if not user.is_active:
            messages.error(request, "This account is inactive.")
            return redirect(reverse('login'))  # Replace 'login' with the appropriate view name

        # Authenticate the user
        user = authenticate(email=email)
        
        return {
            'is_new': False,
            'user': user,
        }
