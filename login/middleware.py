# login/middleware.py
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    Forces login on every view except those explicitly exempted.
    """
    EXEMPT_PREFIXES = ('/static/', '/media/', '/admin/login/')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            login_path = reverse('login')

            if request.path != login_path and not request.path.startswith(self.EXEMPT_PREFIXES):
                return redirect_to_login(request.get_full_path())

        return self.get_response(request)