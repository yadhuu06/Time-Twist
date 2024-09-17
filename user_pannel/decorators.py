from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from functools import wraps

def active_user_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_active:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Your account is inactive. Please contact support.")
    return _wrapped_view
