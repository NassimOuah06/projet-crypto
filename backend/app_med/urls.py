from django.urls import path
from . import views

urlpatterns = [
    path("med/from_user/<int:id>/", views.med_from_user, name="med_from_user"),
    # Med (Médecin) URLs
    path("dashboard/<int:id>/", views.med_dashboard, name="med_dashboard"),
    path("patients/", views.med_get_patients, name="med_get_patients"),
    path("patients/<int:id>/", views.med_get_patient, name="med_get_patient"),
    path("patients/update/<int:id>/", views.med_update_patient, name="med_update_patient"),

    path("dossiers/", views.med_get_dossiers, name="med_get_dossiers"),
    path("dossiers/<int:id>/", views.med_get_dossier, name="med_get_dossier"),
    path("dossiers/add/", views.med_add_dossier, name="med_add_dossier"),
    path("dossiers/update/<int:id>/", views.med_update_dossier, name="med_update_dossier"),
    path("dossiers/delete/<int:id>/", views.med_delete_dossier, name="med_delete_dossier"),

    path("consultations/", views.med_get_consultations, name="med_get_consultations"),
    path("consultations/<int:id>/", views.med_get_consultation, name="med_get_consultation"),
    path("consultations/add/", views.med_add_consultation, name="med_add_consultation"),
    path("consultations/update/<int:id>/", views.med_update_consultation, name="med_update_consultation"),
    path("consultations/delete/<int:id>/", views.med_delete_consultation, name="med_delete_consultation"),

]
