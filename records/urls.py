from django.urls import path
from . import views

urlpatterns = [
    path("", views.record_list, name="record_list"),
    path("<int:order_id>/", views.record_view, name="report_view"),
]