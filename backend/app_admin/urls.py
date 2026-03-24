from django.urls import path
from . import views

urlpatterns = [
    # Admin URLs
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("meds/", views.admin_get_meds, name="admin_get_meds"),
    path("meds/<int:id>/", views.admin_get_med, name="admin_get_med"),
    path("meds/add/", views.admin_add_med, name="admin_add_med"),
    path("meds/delete/<int:id>/", views.admin_delete_med, name="admin_delete_med"),
    path("meds/update/<int:id>/", views.admin_update_med, name="admin_update_med"),

    path("patients/", views.admin_get_patients, name="admin_get_patients"),
    path("patients/<int:id>/", views.admin_get_patient, name="admin_get_patient"),
    path("patients/add/", views.admin_add_patient, name="admin_add_patient"),
    path("patients/delete/<int:id>/", views.admin_delete_patient, name="admin_delete_patient"),
    path("patients/update/<int:id>/", views.admin_update_patient, name="admin_update_patient"),

    path("dossiers/", views.admin_get_dossiers, name="admin_get_dossiers"),
    path("dossiers/<int:id>/", views.admin_get_dossier, name="admin_get_dossier"),
    path("dossiers/delete/<int:id>/", views.admin_delete_dossier, name="admin_delete_dossier"),

    path("consultations/", views.admin_get_consultations, name="admin_get_consultations"),
    path("consultations/<int:id>/", views.admin_get_consultation, name="admin_get_consultation"),
]
