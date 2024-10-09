from django.core.exceptions import ValidationError
from .models import User
from django.contrib import messages, auth
from django.shortcuts import redirect
from django.urls import reverse

def save_user_details(backend, user, response, request, *args, **kwargs):
    if backend.name == 'google-oauth2':
        email = response.get('email')
        first_name = response.get('given_name')
        last_name = response.get('family_name')

        if user:  # If the user is already logged in
            return {
                'is_new': False,
                'user': user,
            }
        
        try:
            # Try to get the user by email
            existing_user = User.objects.get(email=email)
            # Authenticate and log the user in if they exist
            auth.login(request, existing_user, backend='social_core.backends.google.GoogleOAuth2')
            return {
                'is_new': False,
                'user': existing_user,
            }
        except User.DoesNotExist:
            # If user doesn't exist, create a new one
            new_user = User(email=email, first_name=first_name, last_name=last_name)
            new_user.is_active = True  # Activate the new user
            new_user.save()

            # Log the new user in, specifying the backend
            auth.login(request, new_user, backend='social_core.backends.google.GoogleOAuth2')

            return {
                'is_new': True,
                'user': new_user,
            }

        # Handle cases where the user has no first name or last name set
        if not user.first_name or not user.last_name:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        # If the user's account is inactive, display an error message and redirect
        if not user.is_active:
            messages.error(request, "This account is inactive.")
            return redirect(reverse('login'))

    return {
        'is_new': False,
        'user': user,
    }
