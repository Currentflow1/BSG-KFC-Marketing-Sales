from django.contrib.auth import login as auth_login, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages


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

    return render(request, "registration/login.html", {
        "form": form, "next": request.GET.get("next", "")
    })


def first_run_setup(request):
    User = get_user_model()
    if User.objects.filter(is_superuser=True).exists():
        return redirect("login")  # already set up, block re-entry

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email", "")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if not username or not password:
            messages.error(request, "Username and password are required.")
        elif password != confirm:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            messages.success(request, "Admin account created. You can now log in.")
            return redirect("login")

    return render(request, "registration/first_run_setup.html")