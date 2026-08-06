from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="forecast_dashboard"),
    path("product/<int:product_id>/", views.product_forecast, name="product_forecast"),
]