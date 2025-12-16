from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator