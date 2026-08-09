from django.urls import path
from . import views

urlpatterns = [
  path('', views.employee_list, name='employee_list'),
  path("search/", views.employee_search, name="employee_search"),

  path('new/', views.employee_new, name='employee_new'),
  path('<int:id>/edit', views.employee_edit, name='employee_edit'),
  path('<int:id>/delete', views.employee_delete, name='employee_delete'),
]