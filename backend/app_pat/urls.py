from django.urls import path
from . import views

urlpatterns = [
    # Patient URLs
    path("dashboard/<int:id>/", views.pat_dashboard, name="pat_dashboard"),
    
    path("dossiers/", views.pat_get_dossier, name="pat_get_dossier"),
    
    path("consultations/", views.pat_get_consultations, name="pat_get_consultations"),
    path("consultations/<int:id>/", views.pat_get_consultation, name="pat_get_consultation"),
]
