from django.urls import path
from . import views

urlpatterns = [
  path('', views.customer_list, name='customer_list'),
  path('new/', views.customer_new, name='customer_new'),
  path('<int:id>/edit', views.customer_edit, name='customer_edit'),
  path('<int:id>/delete', views.customer_delete, name='customer_delete'),
]