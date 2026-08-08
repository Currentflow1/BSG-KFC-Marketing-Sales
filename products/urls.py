from django.urls import path
from . import views


urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("search/", views.product_search, name="product_search"),

    path("new/", views.product_new, name="product_new"),
    path("<int:id>/edit/", views.product_edit, name="product_edit"),
    path("<int:id>/delete/", views.product_delete, name="product_delete"),
]