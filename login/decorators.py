from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def permission_required_redirect(perm, redirect_url="dashboard"):
    """
    Like Django's @permission_required, but instead of showing a raw
    403 page, redirects the user back to `redirect_url` with a flash
    message explaining why they were blocked.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if not request.user.has_perm(perm):
                messages.error(request, "You don't have permission to do that.")
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator