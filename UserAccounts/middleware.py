from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import logout
from typing import Any
from django.shortcuts import redirect
from django.contrib import messages
from social_core.exceptions import AuthCanceled  
from django.shortcuts import render
from django.http import Http404


class SocialAuthExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, AuthCanceled):
            messages.error(request, "Authentication process canceled.")
            return redirect('home_view')  
        return None