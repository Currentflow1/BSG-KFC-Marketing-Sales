from django.urls import path
from . import views

urlpatterns = [
  path('', views.login, name='login'),
  path("setup/", views.first_run_setup, name="first_run_setup"),
]