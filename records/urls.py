from django.urls import path
from . import views

urlpatterns = [
    path("", views.record_list, name="record_list"),
    path("<int:order_id>/", views.record_view, name="report_view"),
    path('reports/<int:order_id>/export-csv/', views.export_trip_report_csv, name='export_trip_report_csv'),
    path("short-over/", views.short_over_matrix, name="short_over_matrix"),
    path("short-over/export/", views.export_short_over_matrix_csv, name="export_short_over_matrix_csv"),
    path("mret-percentage/", views.mret_percentage_matrix, name="mret_percentage_matrix"),
    path("mret-percentage/export/", views.export_mret_percentage_matrix_csv, name="export_mret_percentage_matrix_csv"),
]