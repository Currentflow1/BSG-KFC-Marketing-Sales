from django.urls import path
from . import views

urlpatterns = [
  path('', views.record_view, name='record_view')
]
