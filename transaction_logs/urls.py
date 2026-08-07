from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='transaction_logs_home'),
]