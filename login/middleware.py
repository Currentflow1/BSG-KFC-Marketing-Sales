# login/middleware.py
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse

class LoginRequiredMiddleware:
    """
    Forces login on every view except those explicitly exempted.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            exempt_urls = [
                reverse('login'),
                '/admin/login/',
            ]
            # allow static/media files through
            exempt_prefixes = ['/static/', '/media/']

            if request.path not in exempt_urls and not any(
                request.path.startswith(p) for p in exempt_prefixes
            ):
                return redirect_to_login(request.get_full_path())

        return self.get_response(request)