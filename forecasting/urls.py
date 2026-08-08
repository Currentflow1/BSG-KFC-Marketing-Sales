from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="forecast_dashboard"),
    path("search/", views.forecasting_search, name="forecasting_search"),
    path("product/<int:product_id>/", views.product_forecast, name="product_forecast"),
]