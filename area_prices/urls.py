from django.urls import path
from . import views

urlpatterns = [
  path('', views.area_price_list, name='area_price_list'),


  path('new/', views.area_price_new, name='area_price_new'),
  path('<int:id>/edit', views.area_price_edit, name='area_price_edit'),
  path('<int:id>/delete', views.area_prices_delete, name='area_price_delete'),

  
  path('new_area/', views.area_new, name='area_new'),
  path('<int:id>/edit_area', views.area_edit, name='area_edit'),
  path('<int:id>/delete_area', views.area_delete, name='area_delete'),
]