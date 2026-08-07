# login/middleware.py
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.shortcuts import redirect


class LoginRequiredMiddleware:
    """
    Forces login on every view except those explicitly exempted.
    Also forces first-run setup if no superuser exists yet.
    """
    EXEMPT_PREFIXES = ('/static/', '/media/', '/admin/login/')

    def __init__(self, get_response):
        self.get_response = get_response
        self._superuser_exists = None  # cached after first check

    def __call__(self, request):
        setup_path = reverse('first_run_setup')
        login_path = reverse('login')

        # Only check DB for superuser existence until one is found,
        # then cache True forever (avoids a query on every request).
        if not self._superuser_exists:
            User = get_user_model()
            self._superuser_exists = User.objects.filter(is_superuser=True).exists()

        if not self._superuser_exists:
            if request.path != setup_path and not request.path.startswith(self.EXEMPT_PREFIXES):
                return redirect(setup_path)
            return self.get_response(request)

        # Normal login-required flow once a superuser exists
        if not request.user.is_authenticated:
            if request.path != login_path and not request.path.startswith(self.EXEMPT_PREFIXES):
                return redirect_to_login(request.get_full_path())

        return self.get_response(request)