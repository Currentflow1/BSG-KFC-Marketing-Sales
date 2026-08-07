from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.conf import settings


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next") or settings.LOGIN_REDIRECT_URL
            return redirect(next_url)
    else:
        form = AuthenticationForm(request)

    return render(request, "registration/login.html", {"form": form, "next": request.GET.get("next", "")})